# TODO: Method to preview image in Jupyter
from typing import Optional, Tuple

from attr import field

from pyinaturalist.constants import CC_LICENSES, PHOTO_INFO_BASE_URL, PHOTO_SIZES, TableRow
from pyinaturalist.converters import format_dimensions, format_license
from pyinaturalist.models import BaseModel, define_model, kwarg


@define_model
class Photo(BaseModel):
    """An observation photo, based on the schema of photos from
    `GET /observations <https://api.inaturalist.org/v1/docs/#!/Observations/get_observations>`_.
    """

    attribution: str = kwarg
    id: int = kwarg
    license_code: str = field(converter=format_license, default=None)  # Enum
    original_dimensions: Tuple[int, int] = field(converter=format_dimensions, default=(0, 0))
    url: str = kwarg
    _url_format: str = field(init=False, repr=False, default=None)

    # Unused attributes
    # flags: List = field(factory=list)

    def __attrs_post_init__(self):
        if not self.url:
            return

        # Get a URL format string to get different photo sizes. Note: default URL may be any size.
        for size in PHOTO_SIZES:
            if f'{size}.' in self.url:
                self._url_format = self.url.replace(size, '{size}')

    @property
    def dimensions_str(self) -> str:
        return f'{self.original_dimensions[0]}x{self.original_dimensions[1]}'

    @property
    def has_cc_license(self) -> bool:
        """Determine if this photo has a Creative Commons license"""
        return self.license_code in CC_LICENSES

    @property
    def info_url(self) -> str:
        return f'{PHOTO_INFO_BASE_URL}/{self.id}'

    @property
    def large_url(self) -> Optional[str]:
        return self.url_size('large')

    @property
    def medium_url(self) -> Optional[str]:
        return self.url_size('medium')

    @property
    def original_url(self) -> Optional[str]:
        return self.url_size('original')

    @property
    def small_url(self) -> Optional[str]:
        return self.url_size('small')

    @property
    def square_url(self) -> Optional[str]:
        return self.url_size('square')

    @property
    def thumbnail_url(self) -> Optional[str]:
        return self.url_size('square')

    def url_size(self, size: str) -> Optional[str]:
        size = size.replace('thumbnail', 'square').replace('thumb', 'square')
        if not self._url_format or size not in PHOTO_SIZES:
            return None
        return self._url_format.format(size=size)

    def open(self, size: str = 'large'):
        """Download and display the image with the system's default image viewer.
        Experimental / requires ``pillow``
        """
        import requests
        from PIL import Image

        url = self.url_size(size)
        if url:
            img = Image.open(requests.get(url, stream=True).raw)
            img.show()

    @property
    def row(self) -> TableRow:
        return {
            'ID': self.id,
            'License': self.license_code,
            'Dimensions': self.dimensions_str,
            'URL': self.original_url,
        }

    def __str__(self) -> str:
        return f'[{self.id}] {self.original_url} ({self.license_code}, {self.dimensions_str})'