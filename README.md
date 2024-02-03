# svd-downloader

This repo allows downloading the entire Saarbruecken Voice Database.

Originally based on (https://github.com/HAMMADIPRO/SVD_downloader), but in it's current form it is almost entirely modified. The changes were made primarily to allow for automatic creation of files, running most fetches in parallel and to break downloading of files and saving list of links into separate steps.

## Installation

```bash
pip install svd-downloader
```

## Running

```bash
python -m svd-downloader <output_directory>
```

### Arguments

- <output_directory>: positional argument, specifies where to download data
- --refetch-links: if links file already exists then refetch all links

## License

This project itself is licensed under the [MIT License](./LICENSE), but the dataset that will be downloaded is licensed licensed under [SVD dataset License](LICENSE).
