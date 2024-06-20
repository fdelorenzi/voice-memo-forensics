# Voice Memo Forensics

Voice Memo Forensics is a forensic analysis tool that compares voice memo recordings in an iTunes backup database (`CloudRecordings.db`) to their corresponding `.m4a` files, and generates a report that indicates any differences between the two.

The tool is specifically designed for forensic use, and can be used to identify signs of tampering or alteration in voice memo recordings.

## Usage

To use the tool, run the following command:

```
python audit_voice_memos.py <db_path> <m4a_path> [--report_file <report_file>]
```

Where:

- `<db_path>` is the path to the `cloudrecordings.db` file in the iTunes backup.
- `<m4a_path>` is the path to the `.m4a` file or folder containing `.m4a` files to compare.
- `<report_file>` is an optional argument that specifies the path to the report file. If not specified, the report will be printed to the console.

## Features

- Compares the duration, creation date, Apple audio digest, major brand, voice memo UUID, and encoder of each `.m4a` file to the corresponding values in the `cloudrecordings.db` file.
- Supports comparison of individual `.m4a` files or entire folders of `.m4a` files.
- Generates a report that indicates any differences between the `.m4a` file and the corresponding values in the `CloudRecordings.db` file.
- Supports saving the report to a file.

## Requirements

- Python 3.6 or higher
- `sqlite3` (included in the Python standard library)

## Installation

1. Clone the repository:
```
git clone https://github.com/fdelorenzi/voice-memo-forensics.git
```
2. Make sure `ffprobe` is installed and available in the system's PATH. It belongs to [FFMPEG](https://ffmpeg.org/download.html)
### Mac OSX
If Homebrew is installed, you can run
```
brew install ffmpeg
```
### Linux
You can install the ffmpeg package according to your Linux distribution and package manager
Example:
```
sudo apt-get install ffmpeg
```


## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
