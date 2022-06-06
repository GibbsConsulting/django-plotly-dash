#
# Monkey patching of register_callback
#

import dash._callback

from dash._callback import (handle_grouped_callback_args,
                            insert_callback,
                            NoUpdate,
                            )
import collections
from functools import wraps

from dash.dependencies import (
    handle_callback_args,
    handle_grouped_callback_args,
    Output,
)
from dash.exceptions import PreventUpdate

from dash._grouping import (
    flatten_grouping,
    make_grouping_by_index,
    grouping_len,
)
from dash._utils import (
    create_callback_id,
    stringify_id,
    to_json,
)

from dash import _validate


def register_callback(
    callback_list, callback_map, config_prevent_initial_callbacks, *_args, **_kwargs
):
    (
        output,
        flat_inputs,
        flat_state,
        inputs_state_indices,
        prevent_initial_call,
    ) = handle_grouped_callback_args(_args, _kwargs)
    if isinstance(output, Output):
        # Insert callback with scalar (non-multi) Output
        insert_output = output
        multi = False
    else:
        # Insert callback as multi Output
        insert_output = flatten_grouping(output)
        multi = True

    output_indices = make_grouping_by_index(output, list(range(grouping_len(output))))
    callback_id = insert_callback(
        callback_list,
        callback_map,
        config_prevent_initial_callbacks,
        insert_output,
        output_indices,
        flat_inputs,
        flat_state,
        inputs_state_indices,
        prevent_initial_call,
    )

    # pylint: disable=too-many-locals
    def wrap_func(func):
        @wraps(func)
        def add_context(*args, **kwargs):
            output_spec = kwargs.pop("outputs_list")
            _validate.validate_output_spec(insert_output, output_spec, Output)

            func_args, func_kwargs = _validate.validate_and_group_input_args(
                args, inputs_state_indices
            )

            func_kwargs = {**func_kwargs,
                           **kwargs}

            # don't touch the comment on the next line - used by debugger
            output_value = func(*func_args, **func_kwargs)  # %% callback invoked %%

            if isinstance(output_value, NoUpdate):
                raise PreventUpdate

            if not multi:
                output_value, output_spec = [output_value], [output_spec]
                flat_output_values = output_value
            else:
                if isinstance(output_value, (list, tuple)):
                    # For multi-output, allow top-level collection to be
                    # list or tuple
                    output_value = list(output_value)

                # Flatten grouping and validate grouping structure
                flat_output_values = flatten_grouping(output_value, output)

            _validate.validate_multi_return(
                output_spec, flat_output_values, callback_id
            )

            component_ids = collections.defaultdict(dict)
            has_update = False
            for val, spec in zip(flat_output_values, output_spec):
                if isinstance(val, NoUpdate):
                    continue
                for vali, speci in (
                    zip(val, spec) if isinstance(spec, list) else [[val, spec]]
                ):
                    if not isinstance(vali, NoUpdate):
                        has_update = True
                        id_str = stringify_id(speci["id"])
                        component_ids[id_str][speci["property"]] = vali

            if not has_update:
                raise PreventUpdate

            response = {"response": component_ids, "multi": True}

            try:
                jsonResponse = to_json(response)
            except TypeError:
                _validate.fail_callback_output(output_value, output)

            return jsonResponse

        callback_map[callback_id]["callback"] = add_context

        return func

    return wrap_func


dash._callback.register_callback = register_callback
