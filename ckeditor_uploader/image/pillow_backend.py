from __future__ import absolute_import

import os
from io import BytesIO

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image, ImageOps

from ckeditor_uploader import utils
from django.utils.encoding import force_text


THUMBNAIL_SIZE = getattr(settings, "THUMBNAIL_SIZE", (75, 75))

def resize(file_path):
    
    print('[resize] updated by KENMINE version=0.05')
    
    image_filename = force_text('{0}{1}').format(*os.path.splitext(file_path))
    image_format = utils.get_image_format(os.path.splitext(file_path)[1])

    print('image_filename=' + str(image_filename))
    
    image = default_storage.open(file_path)
    image = Image.open(image)
    file_format = image.format
    
    width, height = image.size
    
    print('CKEDITOR_IMAGE_MAX_WIDTH=' +str(settings.CKEDITOR_IMAGE_MAX_WIDTH))
    print('CKEDITOR_IMAGE_MAX_HEIGHT=' + str(settings.CKEDITOR_IMAGE_MAX_HEIGHT))
    
    if(settings.CKEDITOR_IMAGE_MAX_WIDTH>0 and settings.CKEDITOR_IMAGE_MAX_HEIGHT>0):

        print('width=' +str(width))
        print('height=' +str(height))
    
        if width>height:
            if width>settings.CKEDITOR_IMAGE_MAX_WIDTH:
                new_width = settings.CKEDITOR_IMAGE_MAX_WIDTH
                new_height = int(new_width/width*height)
        else:
            if height>settings.CKEDITOR_IMAGE_MAX_HEIGHT:
                new_height = settings.CKEDITOR_IMAGE_MAX_HEIGHT
                new_width = int(new_height/height*width)
    else:
        new_width = width
        new_height = height
    
    print('new_width=' +str(new_width))
    print('new_height=' +str(new_height))
    
    NEW_SIZE = (new_width,new_height)
    
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')
    
    imagefit = ImageOps.fit(image, NEW_SIZE, Image.ANTIALIAS)
    tempfile_io = BytesIO()
    imagefit.save(tempfile_io, format=file_format)
    
    newImage = InMemoryUploadedFile(
        tempfile_io,
        None,
        image_filename,
        image_format,
        len(tempfile_io.getvalue()),
        None)
    newImage.seek(0)
    
    default_storage.delete(file_path)
    
    return default_storage.save(image_filename, newImage)

def image_verify(f):
    try:
        Image.open(f).verify()
    except IOError:
        raise utils.NotAnImageException


def create_thumbnail(file_path):
    thumbnail_filename = utils.get_thumb_filename(file_path)
    thumbnail_format = utils.get_image_format(os.path.splitext(file_path)[1])

    image = default_storage.open(file_path)
    image = Image.open(image)
    file_format = image.format

    # Convert to RGB if necessary
    # Thanks to Limodou on DjangoSnippets.org
    # http://www.djangosnippets.org/snippets/20/
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')

    # scale and crop to thumbnail
    imagefit = ImageOps.fit(image, THUMBNAIL_SIZE, Image.ANTIALIAS)
    thumbnail_io = BytesIO()
    imagefit.save(thumbnail_io, format=file_format)

    thumbnail = InMemoryUploadedFile(
        thumbnail_io,
        None,
        thumbnail_filename,
        thumbnail_format,
        len(thumbnail_io.getvalue()),
        None)
    thumbnail.seek(0)

    return default_storage.save(thumbnail_filename, thumbnail)


def should_create_thumbnail(file_path):
    image = default_storage.open(file_path)
    try:
        Image.open(image)
    except IOError:
        return False
    else:
        return utils.is_valid_image_extension(file_path)
