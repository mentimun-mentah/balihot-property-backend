import os, uuid, shutil
from typing import TextIO, Union, Dict, List
from PIL import Image, ImageOps

class MagicImage:
    FILE_NAME = None
    _BASE_DIR = os.path.join(os.path.dirname(__file__),'../static/')

    def __init__(self,file: Union[TextIO,Dict[str,TextIO],List[TextIO]],
            width: int,
            height: int,
            path_upload: str,
            square = True,
            **kwargs):

        self.file = file
        self.width = width
        self.height = height
        self.square = square
        self.path_upload = path_upload
        if 'dir_name' in kwargs:
            self.dir_name = kwargs['dir_name']
        if 'watermark' in kwargs:
            self.watermark = kwargs['watermark']

    def _crop_center(self,pil_img: TextIO, crop_width: int, crop_height: int) -> TextIO:
        img_width, img_height = pil_img.size
        return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

    def _crop_max_square(self,pil_img: TextIO) -> TextIO:
        return self._crop_center(pil_img, min(pil_img.size), min(pil_img.size))

    def _remove_exif_tag(self,pil_img: TextIO) -> TextIO:
        exif = pil_img.getexif()
        # Remove all exif tags
        for k in exif.keys():
            if k != 0x0112:
                exif[k] = None  # If I don't set it to None first (or print it) the del fails for some reason.
                del exif[k]
        # Put the new exif object in the original image
        new_exif = exif.tobytes()
        pil_img.info["exif"] = new_exif
        return pil_img

    def _save_file(self,file: TextIO,**kwargs) -> str:
        # save image
        with Image.open(file) as im:
            # set filename
            ext = im.format.lower()
            filename = uuid.uuid4().hex + '.' + ext
            # crop to center and resize img by width x height
            if self.square:
                img = self._crop_max_square(im).resize((self.width, self.height), Image.LANCZOS)
            else:
                img = self._crop_center(im,self.width,self.height)
            # remove exif tag
            img = self._remove_exif_tag(img)
            # flip image to right path
            img = ImageOps.exif_transpose(img)
            # if watermark exists set watermark
            if hasattr(self,'watermark'):
                img = self._set_watermark(img)

            if 'path' in kwargs:
                img.save(os.path.join(kwargs['path'],filename))
            else:
                img.save(os.path.join(self._BASE_DIR,self.path_upload,filename))

        return filename

    def _set_watermark(self,image: TextIO) -> TextIO:
        check = ['center','topleft','topright','bottomleft','bottomright']
        if self.watermark not in check:
            raise ValueError("Param watermark must be between {}".format(', '.join(check)))

        imageWidth, imageHeight = image.size

        watermark = os.path.join(self._BASE_DIR,'watermark.png')
        if os.path.exists(watermark):
            with Image.open(watermark) as logo:
                logoWidth, logoHeight = logo.size
                if self.watermark == 'center':
                    image.paste(logo,(int((imageWidth - logoWidth) / 2), int((imageHeight - logoHeight) / 2)),logo)
                if self.watermark == 'topleft':
                    image.paste(logo, (0, 0), logo)
                if self.watermark == 'topright':
                    image.paste(logo, (imageWidth - logoWidth, 0), logo)
                if self.watermark == 'bottomleft':
                    image.paste(logo, (0, imageHeight - logoHeight), logo)
                if self.watermark == 'bottomright':
                    image.paste(logo, (imageWidth - logoWidth, imageHeight - logoHeight), logo)

        return image

    def save_image(self) -> 'MagicImage':
        if isinstance(self.file,dict):
            # temp storage to save filename in dict
            files_name = dict()
            for index,file in self.file.items():
                filename = self._save_file(file)
                files_name[index] = filename

            self.FILE_NAME = files_name
        elif isinstance(self.file,list):
            # create directory if file isn't exists
            path = os.path.join(self._BASE_DIR,self.path_upload,self.dir_name)
            if not os.path.exists(path):
                os.mkdir(path)
            # temp storage to save filename in dict
            files_name = dict()
            for index,file in enumerate(self.file):
                filename = self._save_file(file,path=path)
                files_name[index] = filename

            self.FILE_NAME = files_name
        else:
            filename = self._save_file(self.file)
            self.FILE_NAME = filename

    @classmethod
    def delete_image(cls,file: str,path_delete: str) -> None:
        path = os.path.join(cls._BASE_DIR,path_delete,file or ' ')
        if os.path.exists(path):
            os.remove(path)

    @classmethod
    def rename_folder(cls,old_name: str, new_name: str, path_update: str) -> None:
        path = os.path.join(cls._BASE_DIR,path_update,old_name or ' ')
        if os.path.exists(path):
            os.rename(path,os.path.join(cls._BASE_DIR,path_update,new_name))

    @classmethod
    def delete_folder(cls,name_folder: str, path_delete: str) -> None:
        path = os.path.join(cls._BASE_DIR,path_delete,name_folder or ' ')
        if os.path.exists(path):
            shutil.rmtree(path)
