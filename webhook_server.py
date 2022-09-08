# Copyright 2022 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import base64
import copy

from flask import Flask
from flask import jsonify
from flask import request
import jsonpatch

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    request_info = request.json
    obj = request_info['request']['object']
    mod = copy.deepcopy(obj)

    patch_str = ""

    scheduler_name = app.config(['scheduler_name'])
    if mod['metadata'].get('annotations'):
        if mod['metadata']['annotations'].get(app.config['scheduler_label']):
            scheduler_name = mod['metadata']['annotations'].get(
                app.config['scheduler_label'])
    mod['spec']['schedulerName'] = scheduler_name
    patch = jsonpatch.JsonPatch.from_diff(obj, mod)
    patch_str = base64.b64encode(str(patch).encode()).decode()

    admission_review = {
        'apiVersion': request_info['apiVersion'],
        'kind': request_info['kind'],
        'response': {
            'allowed': True,
            'uid': request_info['request']['uid'],
        },
    }

    if patch_str:
        admission_review['response'].update({
            'patch': patch_str,
            'patchType': 'JSONPatch',
        })

    return jsonify(admission_review)


def main():
    parser = argparse.ArgumentParser(
        description='Physics Scheduler and Collocation webhook')
    parser.add_argument(
        '--port', type=int, default=443, help='Port on which to serve.')
    parser.add_argument(
        '--bind-address', default='0.0.0.0',
        help='The IP address on which to listen for the --port port.')
    parser.add_argument(
        '--tls-cert-file', default='cert.pem',
        help='File containing the default x509 Certificate for HTTPS.')
    parser.add_argument(
        '--tls-private-key-file', default='key.pem',
        help='File containing the default x509 private key matching '
             '--tls-cert-file.')
    parser.add_argument(
        '--scheduler-label', default='physics-scheduler',
        help='Label used to point out the scheduler to use.')
    parser.add_argument(
        '--scheduler-name', default='llocality-scheduler',
        help='Default scheduler to use in case no annoations are provided.')
    args = parser.parse_args()

    app.config['scheduler_label'] = args.scheduler_label
    app.config['scheduler_name'] = args.scheduler_name
    app.run(host=args.bind_address, port=args.port,
            ssl_context=(args.tls_cert_file, args.tls_private_key_file))


if __name__ == '__main__':
    main()
