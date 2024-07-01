
# Voice Memo Forensics

Voice Memo Forensics is a forensic analysis tool that compares voice memo recordings in an iTunes backup database (`CloudRecordings.db`) to their corresponding `.m4a` files and generates a report that indicates any differences between the two. Additionally, it includes features for Plist file comparison.

The tool is specifically designed for forensic use and can be used to identify signs of tampering or alteration in voice memo recordings.

## Usage

To use the tool, run the following command:

```
python run audit_voice_memos.py <db_path> <m4a_path> [--report_file <report_file>] [--duration_tolerance <duration_tolerance>]
```

Where:

- `<db_path>` is the path to the `CloudRecordings.db` file in the iTunes backup.
- `<m4a_path>` is the path to the `.m4a` file or folder containing `.m4a` files to compare.
- `<report_file>` is an optional argument that specifies the path to the report file. If not specified, the report will be printed to the console.
- `<duration_tolerance>` is an optional argument that specifies the duration tolerance in seconds. The default is 0.15 seconds.

## Features

- Compares the following attributes of each `.m4a` file to the corresponding values in the `CloudRecordings.db` file:
  - Duration
  - Creation date
  - Voice memo UUID
  - Encoder
  - Plist creation date
  - Plist UUID
  - Plist title

- Supports comparison of individual `.m4a` files or entire folders of `.m4a` files.
- Generates a report that indicates any differences between the `.m4a` file and the corresponding values in the `CloudRecordings.db` file and Plist file.
- Supports saving the report to a file.

### Note on Duration Comparison

Usually, there is a slight difference between the duration stored in the database and the duration calculated from the `.m4a` file. During my tests, a tolerance of 150 microseconds (0.15 seconds) has been acceptable. This tolerance can be adjusted using the optional `--duration_tolerance` field.

## Requirements

- Python 3.6 or higher
- `sqlite3` (included in the Python standard library)
- `poetry` (for dependency management)

## Compatible Devices
- iOS 12+ iPhones / iPad

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/fdelorenzi/voice-memo-forensics.git
    cd voice-memo-forensics
    ```

2. Install dependencies using `poetry`:
    ```sh
    poetry install
    ```

## Running the Tool

To run the tool, use the following command:
```sh
python audit_voice_memos.py path/to/CloudRecordings.db path/to/audio/file(s).mp4 --report_file report-name.txt ì
```

or

```sh
python audit_voice_memos.py path/to/CloudRecordings.db path/to/audio-folder --report_file report-name.txt ìì
```

## Example Report
```plaintext
Comparison of recordings in ..\audio-sample\CloudRecordings.db to m4a files in ..\audio-sample
Timestamp: 2024-07-01 00:09:03.204014

=== M4A Metadata ===
File name: 20240101 hhmmss.m4a
Size: [****OBFUSCATED***] bytes
Duration: 123.111 seconds
Creation date: 2024-01-01 21:31:12+00:00
SHA256 checksum: [****OBFUSCATED***]
Voice memo UUID: [****OBFUSCATED***]
Encoder: com.apple.VoiceMemos (iPhone Version 17.2.1 (Build 21C66))

=== Plist ===
Plist creation date: 2024-01-01 21:31:14+00:00
Plist UUID: [****OBFUSCATED***]
Plist title: Nuovo memo 123

=== Data from Database ===
Creation date: 2024-01-01 21:31:12+00:00
Audio Digest: iPhone Version 17.3.1
Duration: 123.11 seconds

=== Comparison results ===
[ V ] Duration matching (tolerance: 0.15 seconds)
[ V ] Creation date matching (with microsecond set to 0)
[ V ] Voice memo UUID matching
[ V ] Encoder is expected: com.apple.VoiceMemos (iPhone Version 17.2.1 (Build 21C66))
[ V ] Plist creation date matching
[ V ] Plist UUID matching
```

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Reference

This tool is informed by the findings in the following paper:

Zeng, Jinhua, Qiuxiu Lian, and Shaopei Shi. "Forensic originality identification of iPhone’s voice memos." Journal of Physics: Conference Series. Vol. 1345. No. 5. IOP Publishing, 2019.
