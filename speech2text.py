# Copyright (c) 2025 FireRedTeam (https://github.com/FireRedTeam)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import glob
import os

from fireredasr.models.fireredasr import FireRedAsr

parser = argparse.ArgumentParser()
parser.add_argument("--asr_type", type=str, required=True, choices=["aed", "llm"])

# Input / Output
parser.add_argument("--wav_path", type=str)
parser.add_argument("--wav_paths", type=str, nargs="*")
parser.add_argument("--wav_dir", type=str)
parser.add_argument("--wav_scp", type=str)
parser.add_argument("--output", type=str)

# Decode Options
parser.add_argument("--use_gpu", type=int, default=1)
parser.add_argument("--batch_size", type=int, default=1)
parser.add_argument("--beam_size", type=int, default=1)
parser.add_argument("--decode_max_len", type=int, default=0)
# FireRedASR-AED
parser.add_argument("--nbest", type=int, default=1)
parser.add_argument("--softmax_smoothing", type=float, default=1.0)
parser.add_argument("--aed_length_penalty", type=float, default=0.0)
parser.add_argument("--eos_penalty", type=float, default=1.0)
# FireRedASR-LLM
parser.add_argument("--decode_min_len", type=int, default=0)
parser.add_argument("--repetition_penalty", type=float, default=1.0)
parser.add_argument("--llm_length_penalty", type=float, default=0.0)
parser.add_argument("--temperature", type=float, default=1.0)


def main(args):
    wavs = get_wav_info(args)
    fout = open(args.output, "w") if args.output else None

    model = FireRedAsr.from_pretrained(args.asr_type)

    batch_uttid = []
    batch_wav_path = []
    for i, wav in enumerate(wavs):
        uttid, wav_path = wav
        batch_uttid.append(uttid)
        batch_wav_path.append(wav_path)
        if len(batch_wav_path) < args.batch_size and i != len(wavs) - 1:
            continue

        results = model.transcribe(
            batch_uttid,
            batch_wav_path,
            {
                "use_gpu": args.use_gpu,
                "beam_size": args.beam_size,
                "nbest": args.nbest,
                "decode_max_len": args.decode_max_len,
                "softmax_smoothing": args.softmax_smoothing,
                "aed_length_penalty": args.aed_length_penalty,
                "eos_penalty": args.eos_penalty,
                "decode_min_len": args.decode_min_len,
                "repetition_penalty": args.repetition_penalty,
                "llm_length_penalty": args.llm_length_penalty,
                "temperature": args.temperature,
            },
        )

        for result in results:
            print(result)
            if fout is not None:
                fout.write(f"{result['uttid']}\t{result['text']}\n")

        batch_uttid = []
        batch_wav_path = []


def get_wav_info(args):
    """
    Returns:
        wavs: list of (uttid, wav_path)
    """
    if args.wav_path:
        wavs = [(os.path.basename(args.wav_path).replace(".wav", ""), args.wav_path)]
    elif args.wav_paths and len(args.wav_paths) >= 1:
        wavs = [(os.path.basename(p).replace(".wav", ""), p) for p in sorted(args.wav_paths)]
    elif args.wav_scp:
        wavs = [line.strip().split() for line in open(args.wav_scp)]
    elif args.wav_dir:
        wavs = glob.glob(f"{args.wav_dir}/**/*.wav", recursive=True)
        wavs = [(os.path.basename(p).replace(".wav", ""), p) for p in sorted(wavs)]
    else:
        raise ValueError("Please provide valid wav info")
    print(f"#wavs={len(wavs)}")
    return wavs


if __name__ == "__main__":
    args = parser.parse_args()
    print(args)
    main(args)
