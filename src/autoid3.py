import asyncio
import pathlib
import argparse

from id3.auto_id3_worker import AutoID3Worker

NUM_WORKERS = 5

async def detect_mp3s(dir, mp3_queue):
    """Discovers all of the mp3s in a given directory and adds
    to the queue for processing.

    Args:
        dir (str): Directory in which mp3s are searched in.
        mp3_queue (asyncio.Queue): Queue that holds mp3 track file
        paths. 
    """
    for mp3_file in pathlib.Path(dir).glob('*.mp3'):
        await mp3_queue.put(mp3_file)


async def main(dirs, workers):
    """Detects all of the mp3s given the input directories and sends
    them off to the workers for metadata population.

    Args:
        dirs (list(str)): Directories in which mp3s are searched in.
        workers (int): Number of task workers.
    """
    mp3_queue = asyncio.Queue()

    for dir in dirs:
        await detect_mp3s(dir, mp3_queue)
    tasks = []
    
    for _ in range(workers):
        task = asyncio.create_task(AutoID3Worker(mp3_queue).process_track())
        tasks.append(task)
    
    await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AutoID3. MP3 metadata population made easy.')
    parser.add_argument('-d', '--directory', required=True, action='append', help='mp3 source directory', default=[])
    parser.add_argument('-w', '--workers', help='number of workers', default=NUM_WORKERS, type=int)
    args = parser.parse_args()
    
    asyncio.run(main(args.directory, args.workers))
