import sqlite3
import hashlib
import argparse
import datetime
import os
import plistlib
from mutagen.mp4 import MP4

def get_m4a_info(file_path):
    audio = MP4(file_path)
    creation_date = datetime.datetime.fromtimestamp(os.path.getctime(file_path), datetime.timezone.utc)
    
    duration_by_info = audio.info.length
    duration_by_tags = float(audio.tags.get('©dur', [0])[0]) if '©dur' in audio.tags else None
    
    
    #audio_segment = pydub.AudioSegment.from_file(file_path, format='m4a')
    #samples = audio_segment.get_array_of_samples()
    #sample_rate = audio_segment.frame_rate
    #duration_by_samples = len(samples) / sample_rate / audio_segment.channels
    #print(f'Duration by samples (number of samples / sample_rate / channels): {duration_by_samples}')
    #print(f'Sample rate: {sample_rate} Hz')

    file_size = os.path.getsize(file_path)
    

    info = {
        'size': file_size,
        #'sample_rate': sample_rate,
        'duration': duration_by_info,
        'duration_by_tags': duration_by_tags,
        #'duration_by_samples': duration_by_samples,
        'tags': audio.tags,
        'creation_date': creation_date
    }
    return info


def get_db_info(db_path, file_name):
    conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
    c = conn.cursor()
    c.execute('PRAGMA integrity_check')
    if c.fetchone()[0] != 'ok':
        raise Exception('Database integrity check failed')
    c.execute('SELECT Z_PK, ZDURATION, ZDATE, ZAUDIODIGEST, ZUNIQUEID FROM ZCLOUDRECORDING WHERE ZPATH LIKE ?', (f'%{file_name}',))
    return c.fetchone()

def compute_sha1_hash(file_path):
    # Load the m4a file
    with open(file_path, 'rb') as f:
        data = f.read()

    # Compute the SHA-1 hash
    sha1_hash = hashlib.sha1(data).hexdigest()

    return sha1_hash
def calculate_m4a_audio_digest(file_path):
    audio = MP4(file_path)
    audio_data = audio.pprint().encode()
    sha256_hash = hashlib.sha256(audio_data).hexdigest()
    return sha256_hash

def calculate_checksum(file_path):
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()



def compare_recordings(db_path, m4a_path, duration_tolerance):
    comparison_results = []

    file_name = os.path.basename(m4a_path)
    file_name_wo_extension = os.path.splitext(file_name)[0]
    plist_path = os.path.join(os.path.dirname(m4a_path), f'{file_name_wo_extension}.composition/manifest.plist')
    

    db_info = get_db_info(db_path, file_name)
    if db_info is None:
        raise Exception(f'No matching recording found in database for file: {m4a_path}')
    m4a_info = get_m4a_info(m4a_path)
    m4a_sha256_checksum = calculate_checksum(m4a_path)
    m4a_voice_memo_uuid = m4a_info['tags'].get('----:com.apple.iTunes:voice-memo-uuid', [''])[0].decode('utf-8')
    db_checksum = db_info[3].hex()
    db_creation_date = datetime.datetime.fromtimestamp(db_info[2] + 978307200, datetime.timezone.utc)
    
    if os.path.exists(plist_path):
        with open(plist_path, 'rb') as f:
            plist_content = plistlib.load(f)
        
        plist_creation_date = plist_content['RCSavedRecordingCreationDate'].replace(tzinfo=datetime.timezone.utc)
        plist_uuid = plist_content['RCSavedRecordingUUID']
        plist_title = plist_content['RCSavedRecordingTitle']
    else:
        plist_creation_date = None
        plist_uuid = None
        plist_title = None
        comparison_results.append(f'Skipping manifest check as manifest.plist file does not exist.')
    
    comparison_results.append('=== M4A Metadata ===')
    comparison_results.append(f'File name: {file_name}')
    comparison_results.append(f'Size: {m4a_info["size"]} bytes')
    comparison_results.append(f'Duration: {m4a_info["duration"]} seconds')
    if m4a_info['duration_by_tags']:
        comparison_results.append(f'Duration by tags: {m4a_info["duration_by_tags"]} seconds')
    comparison_results.append(f'Creation date: {m4a_info["creation_date"]}')
    comparison_results.append(f'SHA256 checksum: {m4a_sha256_checksum}')
    comparison_results.append(f'Voice memo UUID: {m4a_voice_memo_uuid}')
    comparison_results.append(f'Encoder: {m4a_info["tags"].get("©too", [""])[0]}')


    if plist_creation_date:
        comparison_results.append('=== Plist ===')
        comparison_results.append(f'Plist creation date: {plist_creation_date}')
        comparison_results.append(f'Plist UUID: {plist_uuid}')
        comparison_results.append(f'Plist title: {plist_title}')

    comparison_results.append('=== Data from Database ===')
    comparison_results.append(f'Creation date: {db_creation_date}')
    comparison_results.append(f'Audio Digest: {db_checksum}')
    comparison_results.append(f'Duration: {db_info[1]} seconds')
    

    comparison_results.append(f'=== Comparison results ===')
    duration_difference = abs(db_info[1] - float(m4a_info['duration']))
    if duration_difference <= duration_tolerance:
        comparison_results.append(f'[ V ] Duration matching (tolerance: {duration_tolerance} seconds)')
    else:
        comparison_results.append(f'[ X ] Duration not matching: {db_info[1]} != {m4a_info["duration"]} (difference: {duration_difference} seconds)')
    
    db_creation_date = db_creation_date.replace(microsecond=0).isoformat()
    m4a_creation_date = m4a_info['creation_date'].replace(microsecond=0).isoformat()
    
    if plist_creation_date:
        plist_creation_date = plist_creation_date.isoformat()

    if db_creation_date == m4a_creation_date:

        comparison_results.append('[ V ] Creation date matching (with microsecond set to 0)')
    else:
        comparison_results.append(f'[ X ] Creation date not matching: {db_creation_date} != {m4a_creation_date}')
    
    
    if db_info[4] == m4a_voice_memo_uuid:
        comparison_results.append('[ V ] Voice memo UUID matching')
    else:
        comparison_results.append(f'[ X ] Voice memo UUID not matching: {db_info[4]} != {m4a_voice_memo_uuid}')
    
    if '©too' in m4a_info['tags'] and m4a_info['tags']['©too'][0].startswith('com.apple.VoiceMemos'):
        comparison_results.append(f"[ V ] Encoder is expected: {m4a_info['tags']['©too'][0]}")
    else:
        comparison_results.append(f"[ X ] Encoder is not expected: {m4a_info['tags']['©too'][0]}")

        
    if plist_creation_date:
        if plist_creation_date == m4a_creation_date:
            comparison_results.append('[ V ] Plist creation date matching (with microsecond set to 0)')
        else:
            comparison_results.append(f'[ X ] Plist creation date not matching: {plist_creation_date} != {m4a_creation_date}')
        
        if plist_uuid == m4a_voice_memo_uuid:
            comparison_results.append('[ V ] Plist UUID matching')
        else:
            comparison_results.append(f'[ X ] Plist UUID not matching: {plist_uuid} != {m4a_voice_memo_uuid}')
    
    return '\n'.join(comparison_results)


def main():
    parser = argparse.ArgumentParser(description='Compare a recording in a cloudrecordings.db file to an m4a file')
    parser.add_argument('db_path', help='path to the cloudrecordings.db file')
    parser.add_argument('m4a_path', help='path to the m4a file or folder containing m4a files')
    parser.add_argument('--duration_tolerance', type=float, default=0.15, help='duration tolerance in seconds (default: 0.15)')
    parser.add_argument('--report_file', help='path to the report file')

    args = parser.parse_args()

    if not os.access(args.db_path, os.R_OK):
        raise Exception(f'Cannot read database file: {args.db_path}')

    if os.path.isdir(args.m4a_path):
        m4a_files = [os.path.abspath(os.path.join(args.m4a_path, f)) for f in os.listdir(args.m4a_path) if f.endswith('.m4a')]
    else:
        m4a_files = [os.path.abspath(args.m4a_path)]

    for m4a_file in m4a_files:
        if not os.access(m4a_file, os.R_OK):
            raise Exception(f'Cannot read m4a file: {m4a_file}')

    report = f'Comparison of recordings in {args.db_path} to m4a files in {args.m4a_path}\n'
    report += f'Timestamp: {datetime.datetime.now()}\n'
    print(report)
    
    for m4a_file in m4a_files:
        differences = compare_recordings(args.db_path, m4a_file, args.duration_tolerance)
        print(differences)
        print('--------------------------')
        report += f'\n{m4a_file}:\n{differences}\n'

    if args.report_file is not None:
        with open(args.report_file, 'w') as f:
            f.write(report)


if __name__ == '__main__':
    main()
