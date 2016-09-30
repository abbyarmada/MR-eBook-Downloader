import MrDeDownloader


if __name__ == "__main__":
    MrDeDownloader.init()
    MrDeDownloader.clean_up()
    MrDeDownloader.create_needed_files()

    MrDeDownloader.load_from_jsonfile()

    MrDeDownloader.download_ebook_list()

    MrDeDownloader.get_ebook_threads()

    MrDeDownloader.download_ebook_threads()

    MrDeDownloader.get_ebook_links()

    MrDeDownloader.check_for_updates()

    MrDeDownloader.download_ebooks()

    MrDeDownloader.update_jsonfile()

    MrDeDownloader.write_no_ebook_founds()

    MrDeDownloader.close_downloader()

    MrDeDownloader.clean_up()

    print('Script says BYE')
