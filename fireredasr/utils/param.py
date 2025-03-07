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

import logging

import torch


def count_model_parameters(model):
    if not isinstance(model, torch.nn.Module):
        return 0, 0
    name = f"{model.__class__.__name__} {model.__class__}"
    num = sum(p.numel() for p in model.parameters() if p.requires_grad)
    size = num * 4.0 / 1024.0 / 1024.0  # float32, MB
    logging.info(f"#param of {name} is {num} = {size:.1f} MB (float32)")
    return num, size
