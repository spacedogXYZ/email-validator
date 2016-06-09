from flask import Blueprint, request, jsonify, make_response
from decorator import crossdomain

import flanker.addresslib.address
import flanker.addresslib.corrector

address = Blueprint('address', __name__, url_prefix='/address')


@address.route('/validate')
@crossdomain(origin='*')
def validate_address():
    arg_address = request.args.get('address')
    if not arg_address:
        return make_response(jsonify({'error': 'address parameter required'}), 400)

    validated = flanker.addresslib.address.validate_address(arg_address)
    if validated is None:
        response = {'is_valid': False}
    else:
        response = {
            'is_valid': True,
            'parts': {
                'local_part': validated.mailbox,
                'domain': validated.hostname
            },
            'address': validated.address
        }
        suggested_hostname = flanker.addresslib.corrector.suggest(validated.hostname)
        if suggested_hostname is not validated.hostname:
            response['did_you_mean'] = '%s@%s' % (validated.mailbox, suggested_hostname)
    return make_response(jsonify(response), 200)
