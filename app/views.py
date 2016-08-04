from flask import Blueprint, current_app, request, jsonify, make_response
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

    validated, metrics = flanker.addresslib.address.validate_address(arg_address, metrics=True, mx_lookup=False)
    current_app.metrics.update(metrics)

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
        if suggested_hostname != validated.hostname:
            response['did_you_mean'] = '%s@%s' % (validated.mailbox, suggested_hostname)
    return make_response(jsonify(response), 200)
