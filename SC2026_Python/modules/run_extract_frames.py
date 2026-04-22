import sys
import argparse
import shutil

from loguru import logger
from pathlib import Path, PurePath

import common
import version as V
import SCDecoder
import json

def extract_frames(start : int, end : int):
    logger.info(f"extract_frames()")

    # 컨테이너 내부에 항상 고정된 위치에 폴더 위치
    logger.info(f"SCENE_DIR: {common.SCENE_DIR} {Path(common.SCENE_DIR).absolute()}")    
    logger.info(f"OUTPUT_DIR: {common.OUTPUT_DIR} {Path(common.OUTPUT_DIR).absolute()}")

    path_output = Path(common.OUTPUT_DIR)
    path_output.mkdir(parents=True, exist_ok=True)
    
    decoder = SCDecoder.SCDecoder()
    decoder.Initialize(common.SCENE_DIR + "/Video", common.SCENE_DIR + "/Image", start, end)
    decoder.DoDecoding()    

    data = {}
    data["start_frame"] = decoder.GetStartFrame()
    data["end_frame"] = decoder.GetEndFrame()
    with open(path_output / "extract_frames_result.json", "w") as file:
        json.dump(data, file, indent=4, sort_keys=True)

    decoder.Finalize()
    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"ETRI Spatial Computing Engine v{V.VERSION}")
    parser.add_argument('--start_frame', type=int, default=None, help='Specify start frame number.')
    parser.add_argument('--end_frame', type=int, default=None, help='Specify end frame number')
    args = parser.parse_args()
    try:
        extract_frames(args.start_frame, args.end_frame)

        logger.info("Success")
        sys.exit(0)

    except Exception as ex:
        # 에러 발생시 로그 출력하고, exit_code를 0이 아닌 값으로 설정
        logger.error(ex)
        sys.exit(1)
