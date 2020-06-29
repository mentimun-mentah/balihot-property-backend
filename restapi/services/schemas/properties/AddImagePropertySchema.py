import os
from PIL import Image
from marshmallow import Schema, fields, ValidationError

class ImageField(fields.Field):
    _ALLOW_FILE_EXT = ['jpg','png','jpeg']
    _MAX_FILE_SIZE = 4 * 1024 * 1024  # 4 Mb

    def _deserialize(self, value, attr, data, **kwargs):
        # extract data
        data = data.getlist('images')

        for index,value in enumerate(data,1):
            if not value.filename:
                raise ValidationError("Missing data[{}] for required field.".format(index))

            # check valid image
            try:
                with Image.open(value) as img:
                    if img.format.lower() not in self._ALLOW_FILE_EXT and img.mode != 'RGB':
                        raise Exception("Image[{}] must be {}".format(index,'|'.join(self._ALLOW_FILE_EXT)))
            except Exception as err:
                err = str(err)
                if "cannot identify image file" in err:
                    err = "Cannot identify image[{}] file".format(index)
                raise ValidationError(err)

            # check size image
            value.seek(0,os.SEEK_END)
            size = value.tell()

            if size > self._MAX_FILE_SIZE:
                raise ValidationError("Image[{}] cannot grater than 4 Mb".format(index))

            value.seek(0)

        return data

class AddImagePropertySchema(Schema):
    images = ImageField(required=True)
