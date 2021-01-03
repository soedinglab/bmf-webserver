from bmf_tool.utils import file_validator
from tempfile import NamedTemporaryFile

def check_input_file(job, form, rq_files, field_name):

    success = False
    err = None

    with NamedTemporaryFile('wb+') as tmp_file:
        for chunk in rq_files[field_name].chunks():
            tmp_file.write(chunk)
        tmp_file.flush()
        try:
            success = file_validator(tmp_file.name, job.input_type, first_n=10)
        except ValueError as exc:
            err = f'File validation error: {str(exc)}'
        except:
            err = f'something went wrong! the input file {field_name} did not pass validation check'

    if not success:
        form.add_error(field_name, err)
        return False
    return True