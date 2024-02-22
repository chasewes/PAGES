"""
Download the clips within the MusicCaps dataset from YouTube.

Requires:
    - ffmpeg
    - yt-dlp
    - datasets[audio]
    - torchaudio
"""
import subprocess
import os
from pathlib import Path

from datasets import load_dataset, Dataset, Audio
import pandas as pd

dataset_path = 'google/MusicCaps'


# https://www.youtube.com/watch?v=MJrEkTEkE4Q

def download_clip(
    video_identifier,
    output_filename,
    start_time,
    end_time,
    tmp_dir='/tmp/musiccaps',
    num_attempts=5,
    url_base='https://www.youtube.com/watch?v='
):
    status = False

    command = f"""
        yt-dlp --quiet --no-warnings -x --audio-format wav -f bestaudio -o "{output_filename}" "{url_base}{video_identifier}" 
    """.strip()

# --download-sections "*{start_time}-{end_time}"

    attempts = 0
    while True:
        try:
            output = subprocess.check_output(command, shell=True,
                                                stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            attempts += 1
            if attempts == num_attempts:
                return status, err.output
        else:
            break

    # Check if the video was successfully saved.
    status = os.path.exists(output_filename)
    print("status: ", status)
    return status, 'Downloaded'


def main(
    data_dir: str,
    sampling_rate: int = 44100,
    limit: int = None,
    num_proc: int = 1,
    writer_batch_size: int = 1000,
):
    """
    Download the clips within the MusicCaps dataset from YouTube.

    Args:
        data_dir: Directory to save the clips to.
        sampling_rate: Sampling rate of the audio clips.
        limit: Limit the number of examples to download.
        num_proc: Number of processes to use for downloading.
        writer_batch_size: Batch size for writing the dataset. This is per process.
    """

    # ds = load_dataset(dataset_path, split='train')
    ds = pd.DataFrame({'ytid': ['MJrEkTEkE4Q']})
    ds = Dataset.from_pandas(ds)
    if limit is not None:
        print(f"Limiting to {limit} examples")
        ds = ds.select(range(limit))

    data_dir = Path(data_dir)
    data_dir.mkdir(exist_ok=True, parents=True)

    def process(example):
        outfile_path = str(data_dir / f"{example['ytid']}.wav")
        status = True
        if not os.path.exists(outfile_path):
            # print("Gonna try to download something to ", outfile_path)
            status = False
            status, log = download_clip(
                example['ytid'],
                outfile_path,
                'strt', 'end'
                # example['start_s'],
                # example['end_s'],
            )
            # print("status: ", status)
            # print("log: ", log)
        # else: 
        #     print(f"skipping file {outfile_path}")

        example['audio'] = outfile_path
        example['download_status'] = status
        return example

    return ds.map(
        process,
        num_proc=num_proc,
        writer_batch_size=writer_batch_size,
        keep_in_memory=False
    ).cast_column('audio', Audio(sampling_rate=sampling_rate))


if __name__ == '__main__':
    ds = main(
        './music_data',
        
        sampling_rate=44100,
        limit=None,
        # num_proc=16,
        num_proc=1,
        writer_batch_size=1000,
    )