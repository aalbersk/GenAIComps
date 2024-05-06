# Copyright (c) 2024 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os

import requests

from comps import RerankingInputDoc, RerankingOutputDoc, opea_microservices, register_microservice


@register_microservice(
    name="opea_service@reranking_tgi_gaudi",
    expose_endpoint="/v1/reranking",
    port=8040,
    input_datatype=RerankingInputDoc,
    output_datatype=RerankingOutputDoc,
)
def reranking(input: RerankingInputDoc) -> RerankingOutputDoc:
    docs = [doc.text for doc in input.passages]
    url = tei_reranking_endpoint + "/rerank"
    data = {"query": input.query, "texts": docs}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(data), headers=headers)
    response_data = response.json()
    best_response = max(response_data, key=lambda response: response["score"])
    res = RerankingOutputDoc(query=input.query, doc=input.passages[best_response["index"]])
    return res


if __name__ == "__main__":
    tei_reranking_endpoint = os.getenv("TEI_RERANKING_ENDPOINT", "http://localhost:8080")
    opea_microservices["opea_service@reranking_tgi_gaudi"].start()
