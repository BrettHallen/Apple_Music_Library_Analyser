##############################
# iTunes Library Analyser    #
# Brett Hallen, 26/Feb/2026  #
# Requires mutagen library:  #
#    pip install mutagen     #
##############################

import os
import time
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
    # Initialise counters and accumulators
    total_files = 0
    file_types = defaultdict(int)    # e.g., {'mp3': 10, 'm4a': 15}
    bitrates = defaultdict(int)      # Count occurrences of each bitrate
    sample_rates = defaultdict(int)  # Count occurrences of each sample rate
    total_size_bytes = 0
    media_types = defaultdict(int)   # e.g., {'audio': 100, 'video': 5} – basic classification
    bit_depths = defaultdict(int)    # e.g., {16: 200, 24: 5}
    # Supported audio/video extensions
    supported_extensions = ('.mp3', '.m4a', '.aac', '.wav', '.aiff', '.flac', '.mp4', '.m4v')

    if not os.path.exists(library_path):
        print(f"!! ERROR: Library path not found:")
        print(f"     '{library_path}' does not exist.")
        print("   Please check the path and update it in the script.")
        print("   Common locations:")
        print("     /Users/<your name>/Music/Music/Media.localized/Music")
        print("     /Users/<your name>/Music/Music/Media")
        print("   Other possbilities (i.e. iTunes era):")
        print("     /Users/<your name>/Music/iTunes/iTunes Music/Music")
        print("   Or if it's on an external drive:")
        print("     /Volumes/<drive name>/Users/<your name>/Music/iTunes/iTunes Music/Music")
        print()
        exit(1)

    if not os.path.isdir(library_path):
        print(f"!! ERROR: '{library_path}' exists but is not a directory.")
        print("   Please provide a valid folder path containing your music files.")
        print()
        exit(1)

    print(f"Processing: {library_path}")
    
    # Walk through the directory
    for root, dirs, files in os.walk(library_path):
        for file in files:
            if file.lower().endswith(supported_extensions):
                total_files += 1
                file_path = os.path.join(root, file)
                if total_files % 100 == 0:
                    print(".", end="", flush=True)
                # File type by extension (e.g., MP3, ALAC via .m4a – note: .m4a can be AAC or ALAC)
                ext = os.path.splitext(file)[1][1:].upper()  # e.g., 'MP3'
                if ext == 'M4A':  # Rough guess: ALAC if lossless, but we'd need metadata for precision
                    ext = 'M4A (AAC)'
                file_types[ext] += 1

                # Media type (audio vs video – basic check by extension)
                if file.lower().endswith(('.mp4', '.m4v')):
                    media_types['Video'] += 1
                else:
                    media_types['Audio'] += 1

                # Size
                total_size_bytes += os.path.getsize(file_path)

                # Metadata: bitrate and sample rate (using torchaudio)
                try:
                    audio = File(file_path)
                    if 'M4A' in ext.upper():
                        if hasattr(audio.info, 'codec') and 'alac' in str(audio.info.codec).lower():
                            file_types['ALAC'] += 1  # re-count as ALAC instead of generic M4A
                            file_types['M4A (AAC)'] -= 1  # adjust generic count
                        elif hasattr(audio.info, 'bitrate') and audio.info.bitrate < 1000000:  # rough lossless check
                            # ALAC often higher effective rate, but bitrate field may be avg
                            pass
                    if audio is not None and hasattr(audio, 'info'):
                        # Sample rate
                        if hasattr(audio.info, 'sample_rate') and audio.info.sample_rate:
                            sr = int(audio.info.sample_rate)
                            sample_rates[sr] += 1
                        # Bitrate (in kbps)
                        if hasattr(audio.info, 'bitrate') and audio.info.bitrate > 0:
                            br = audio.info.bitrate // 1000
                            bitrates[br] += 1
                        else:
                            # Smarter fallback based on format
                            if 'MP3' in ext.upper():
                                bitrates[192] += 1  # common average for older MP3s
                            elif 'ALAC' in ext.upper() or 'M4A' in ext.upper():
                                bitrates[1411] += 1  # assume CD-quality lossless if no bitrate read
                            else:
                                bitrates["Unknown"] += 1
                        # Bit depth (bits per sample)
                        if hasattr(audio.info, 'bits_per_sample') and audio.info.bits_per_sample:
                            bd = int(audio.info.bits_per_sample)
                            bit_depths[bd] += 1
                        else:
                            if 'MP3' in ext.upper():
                                bit_depths[16] += 1  # MP3 is effectively 16-bit
                            elif 'M4A' in ext.upper():
                                bit_depths["Unknown (likely 16-bit AAC)"] += 1
                            else:
                                bit_depths["Unknown / N/A (likely 16-bit)"] += 1
                except Exception as e:
                    print(f"\n!! Skipping metadata for {file}: {e}")

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
        print(f"   321-1411 kbps:     {mid1_count:>5}")
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
print("# 26/Feb/2026                     #")
print("###################################")
print()

# Set your iTunes/Music library path here:
# On my Mac (M2) that came with Music application:
# library_path = "/Users/brett/Music/Music/Media.localized/Music" 
# On my Mac (Intel) that inherited the library I first created on original iMac G4 in 2001-ish:
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
