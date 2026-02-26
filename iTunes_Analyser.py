##############################
# iTunes Library Analyser    #
# Brett Hallen, 26/Feb/2026  #
# Requires mutagen library:  #
#    pip install mutagen     #
##############################

import os
import time
import csv
from collections import defaultdict
# mutagen might not be installed, let's check
try:
    from mutagen import File
except ImportError:
    print()
    print("!! ERROR: The 'mutagen' library is not installed.")
    print("   Please install it by running:")
    print("      pip install mutagen")
    print("   or")
    print("      pip3 install mutagen")
    print()
    exit(1)  # or sys.exit(1) if you import sys

def analyse_music_library(library_path):
    # Initialise counters...
    total_files = 0
    file_types = defaultdict(int)
    bitrates = defaultdict(int)
    sample_rates = defaultdict(int)
    total_size_bytes = 0
    media_types = defaultdict(int)
    bit_depths = defaultdict(int)
    supported_extensions = ('.mp3', '.m4a', '.aac', '.wav', '.aiff', '.flac', '.mp4', '.m4v')

    # Prepare CSV files (overwrite every run)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    success_csv = os.path.join(script_dir, "iTunes_library_contents.csv")
    error_csv   = os.path.join(script_dir, "iTunes_library_errors.csv")

    success_header = ["Artist", "Album", "Song", "File Type", "Bitrate", "Sample Rate", "Sample size", "File Path"]
    error_header   = ["Artist", "Album", "Song", "File Type", "Bitrate", "Sample Rate", "Sample size", "File Path", "Error"]

    # Open files
    success_file = open(success_csv, 'w', newline='', encoding='utf-8')
    error_file   = open(error_csv,   'w', newline='', encoding='utf-8')

    success_writer = csv.writer(success_file)
    error_writer   = csv.writer(error_file)

    # Always write headers at the start
    success_writer.writerow(success_header)
    error_writer.writerow(error_header)

    # Validation & start
    if not os.path.exists(library_path):
        print(f"!! ERROR: Library path not found: '{library_path}'")
        success_file.close()
        error_file.close()
        exit(1)

    if not os.path.isdir(library_path):
        print(f"!! ERROR: '{library_path}' is not a directory.")
        success_file.close()
        error_file.close()
        exit(1)

    print(f"Processing: {library_path}")

    # Main scan loop
    for root, dirs, files in os.walk(library_path):
        for file in files:
            if file.lower().endswith(supported_extensions):
                total_files += 1
                file_path = os.path.join(root, file)
                if total_files % 100 == 0:
                    print(".", end="", flush=True)

                ext = os.path.splitext(file)[1][1:].upper()
                display_ext = ext
                if ext == 'M4A':
                    display_ext = 'M4A (AAC)'

                file_types[display_ext] += 1

                if file.lower().endswith(('.mp4', '.m4v')):
                    media_types['Video'] += 1
                else:
                    media_types['Audio'] += 1

                total_size_bytes += os.path.getsize(file_path)

                # Default values for CSV
                artist = ""
                album  = ""
                title  = file  # fallback to filename
                bitrate_val  = ""
                sr_val       = ""
                bd_val       = ""
                error_msg    = ""

                # Default values for CSV (safe defaults that always exist)
                artist = ""
                album  = ""
                title  = file  # fallback to filename
                bitrate_str = ""          # ← safe default
                sr_str      = ""          # ← safe default
                bd_str      = ""          # ← safe default

                try:
                    audio = File(file_path)
                    if audio is not None:
                        tags = audio.tags or {}

                        def get_tag_value(key1, key2=None):
                            tag = tags.get(key1) or (tags.get(key2) if key2 else None)
                            if tag:
                                if isinstance(tag, list) and tag:
                                    return str(tag[0]).strip()
                                elif hasattr(tag, 'text') and tag.text:
                                    return str(tag.text[0]).strip() if isinstance(tag.text, list) else str(tag.text).strip()
                                else:
                                    return str(tag).strip()
                            return ""

                        artist = get_tag_value('TPE1', '©ART')
                        album  = get_tag_value('TALB', '©alb')
                        title  = get_tag_value('TIT2', '©nam') or file

                        # ALAC detection & re-count
                        if 'M4A' in ext:
                            if hasattr(audio.info, 'codec') and 'alac' in str(audio.info.codec).lower():
                                file_types['ALAC'] += 1
                                file_types['M4A (AAC)'] -= 1

                        if hasattr(audio, 'info'):
                            # Sample rate
                            if hasattr(audio.info, 'sample_rate') and audio.info.sample_rate:
                                sr = int(audio.info.sample_rate)
                                sr_str = f"{sr / 1000:.1f} kHz" if sr >= 1000 else f"{sr} Hz"
                                sample_rates[sr] += 1

                            # Bitrate
                            if hasattr(audio.info, 'bitrate') and audio.info.bitrate > 0:
                                br = audio.info.bitrate // 1000
                                bitrate_str = f"{br} kbps"
                                bitrates[br] += 1
                            else:
                                if 'MP3' in ext:
                                    bitrates[192] += 1
                                    bitrate_str = "192 kbps"
                                elif 'ALAC' in ext or 'M4A' in ext:
                                    bitrates[1411] += 1
                                    bitrate_str = "1411 kbps"
                                else:
                                    bitrates["Unknown"] += 1
                                    bitrate_str = "Unknown"

                            # Bit depth
                            if hasattr(audio.info, 'bits_per_sample') and audio.info.bits_per_sample:
                                bd = int(audio.info.bits_per_sample)
                                bd_str = f"{bd}-bit"
                                bit_depths[bd] += 1
                            else:
                                if 'MP3' in ext:
                                    bit_depths[16] += 1
                                    bd_str = "16-bit"
                                else:
                                    bit_depths["Unknown"] += 1
                                    bd_str = "Unknown"

                    # Success → write formatted values
                    success_writer.writerow([
                        artist,
                        album,
                        title,
                        display_ext,
                        bitrate_str,
                        sr_str,
                        bd_str,
                        file_path
                    ])

                except Exception as e:
                    error_msg = str(e)
                    print(f"\n!! Skipping metadata for {file}: {error_msg}")

                    # Error → write what we have (may be defaults or partial)
                    error_writer.writerow([
                        artist,
                        album,
                        title,
                        display_ext,
                        bitrate_str,     # safe even if not set
                        sr_str,
                        bd_str,
                        file_path,
                        error_msg
                    ])

                    # Write to success CSV
                    success_writer.writerow([
                        artist.strip(),
                        album.strip(),
                        title.strip(),
                        display_ext,
                        bitrate_str,
                        sr_str,
                        bd_str,
                        file_path
                    ])

                except Exception as e:
                    error_msg = str(e)
                    print(f"\n!! Skipping metadata for {file}: {error_msg}")

                    # Write to error CSV (what we know + error)
                    error_writer.writerow([
                        artist.strip() or "",
                        album.strip() or "",
                        title.strip(),
                        display_ext,
                        "",
                        "",
                        "",
                        file_path,
                        error_msg
                    ])

    # Close CSV files
    success_file.close()
    error_file.close()

    # Output results
    print()
    print()

    # [1] File count
    print(f">> File count:        {total_files:>5}")

    # [2] Different file types (MP3, AAC, etc.)
    print(">> File types:")
    # Sort file types alphabetically for consistency
    for ext, count in sorted(file_types.items()):
        print(f"   {ext:<18} {count:>5}")  # left-align extension, right-align count

    # [3] Output bitrates found
    # We'll output the common/normal ones separately: 64/128/160/192/256/320/1411/2116
    # Then lump the other odds ones into bins, otherwise we'll have a long list one 1-count files
    print(">> Bitrates:")
    # Collect counts for the specific common low bitrates
    common_low = {64: bitrates.get(64, 0),
                  128: bitrates.get(128, 0),
                  160: bitrates.get(160, 0),
                  192: bitrates.get(192, 0),
                  256: bitrates.get(256, 0),
                  320: bitrates.get(320, 0)}
    # Sum everything ≤320 that is NOT one of the common ones
    other_low_count = 0
    for br, count in bitrates.items():
        if isinstance(br, int) and br <= 320 and br not in common_low:
            other_low_count += count
    # Now print only the interesting ones (in logical order)
    for br in [64, 128, 160, 192, 256, 320]:
        if common_low[br] > 0:
            print(f"   {br:>3} kbps:          {common_low[br]:>5}")
    # Other low bitrates lumped together
    if other_low_count > 0:
        print(f"   <320 kbps:         {other_low_count:>5}")
    # Grouped ranges (only numeric keys)
    numeric_bitrates = {k: v for k, v in bitrates.items() if isinstance(k, int)}
    mid1_count = sum(count for br, count in numeric_bitrates.items() if 321 <= br <= 1410)
    exact_1411 = numeric_bitrates.get(1411, 0)
    mid2_count = sum(count for br, count in numeric_bitrates.items() if 1412 <= br <= 2115)
    exact_2116 = numeric_bitrates.get(2116, 0)
    high_count = sum(count for br, count in numeric_bitrates.items() if br > 2116)
    if mid1_count > 0:
        print(f"   321-1412 kbps:     {mid1_count:>5}")
    if exact_1411 > 0:
        print(f"   1411 kbps:         {exact_1411:>5}")
    if mid2_count > 0:
        print(f"   1412-2115 kbps:    {mid2_count:>5}")
    if exact_2116 > 0:
        print(f"   2116 kbps:         {exact_2116:>5}")
    if high_count > 0:
        print(f"   >2116 kbps:        {high_count:>5}")
    # Fallback/unknown at bottom
    string_bitrates = {k: v for k, v in bitrates.items() if isinstance(k, str)}
    if string_bitrates:
        for key, count in sorted(string_bitrates.items()):
            print(f"      {key:<12}    {count:>5}")

    # [4] Sample rates, i.e. 44.1kHz, 48kHz
    print(">> Sample rates:")
    for sr, count in sorted(sample_rates.items()):
        print(f"   {sr:>6} Hz:         {count:>5}")

    # [5] Bit depths, i.e. 16/24/32 bit
    print(">> Sample size:")
    known = {k: v for k, v in bit_depths.items() if isinstance(k, int)}
    for bd in sorted(known):
        print(f"   {bd:>2}-bit:            {known[bd]:>5}")
    unknown = {k: v for k, v in bit_depths.items() if isinstance(k, str)}
    for bd in sorted(unknown):
        print(f"   {bd:<20} {unknown[bd]:>5}")

    # [6] Audio or video file count
    print(">> Types of files:")
    for mtype, count in sorted(media_types.items()):
        print(f"   {mtype:<5}:             {count:>5}")

    # [7] Total size of all files
    print(f">> Total size: {total_size_bytes / (1024 ** 3):>2.2f}GB "
          f"({total_size_bytes / (1024 ** 2):>2.2f}MB)")

#################
# Main function #
#################
print()
print("###################################")
print("# Brett's iTunes Library Analyser #")
print("#                     27/Feb/2026 #")
print("###################################")
print()

# Set your iTunes/Music library path here:
# On my Mac (M2) that came with Music application:
# library_path = "/Users/brett/Music/Music/Media.localized/Music"
# On my Mac (Intel) that inherited the library I first created on my original iMac G4 in 2002-ish:
library_path = "/Volumes/Hollie Data/Users/brett/Music/iTunes/iTunes Music/Music"
# Let's capture how long it takes us
start_time = time.time()
analyse_music_library(library_path)
elapsed = time.time() - start_time
minutes = int(elapsed // 60)
seconds = elapsed % 60
if elapsed < 1:
    print(">> Processing time: <1 sec")
elif minutes > 0:
    print(f">> Processing time: {minutes} min {seconds:.0f} sec")
else:
    print(f">> Processing time: {seconds:.1f} sec")
# Final print
print()
