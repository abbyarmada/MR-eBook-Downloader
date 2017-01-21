import sys
import functools
import json
import re
from concurrent import futures
import certifi
import urllib3
import ListHTMLParser
import ThreadHTMLParser
from pathlib import Path
# import multiprocessing

VERSION = ['1', '2', '1']

temp_path = Path('./temp/')
threads_path = Path('./temp/threads/')
download_path = Path('./ebooks/')
update_config_path = Path("./update.data")
using_cores = 4  # multiprocessing.cpu_count()

downloader = urllib3.HTTPSConnectionPool('www.mobileread.com', maxsize=using_cores, cert_reqs='CERT_REQUIRED',
                                         ca_certs=certifi.where())
format_list = ['epub', 'mobi', 'lrf', 'imp', 'pdf', 'lit', 'azw', 'azw3', 'rar', 'lrx']
thread_list = []
ebook_link_dict = {}  # id: (name, time)
ebook_link_dict_old = {}  # id: (name, time)
ebook_download_list = []  # (id, name)
download_succeed_list = []  # id
download_failed_list = []  # id
not_found_ebooks_thread = []  # thread
done_links = 0


def about():
    """
    About methode, displays some information.
    :return:
    """
    print('== ABOUT ==')
    print("Version: " + VERSION[0] + '.' + VERSION[1] + '.' + VERSION[2])
    print("Web: https://github.com/IceflowRE/MR-eBook-Downloader")
    print("Bitte teilt mir jeden Fehler mit! - Please report any bug!")
    print()


def init():
    """
    Initializes the needed global variables to proceed the installation.
    :return:
    """
    print('== INITIALIZE APPLICATION ==')

    if sys.version_info <= (3, 6):
        sys.exit('Only Python 3.6 or greater is supported. You are using:' + str(sys.version_info))

    ebook_link_dict['wikilist_date'] = 0


def check_for_app_updates():
    print('== CHECK FOR APPLICATION UPDATES ==')

    https = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    ver = https.urlopen('GET', 'https://raw.githubusercontent.com/IceflowRE/MR-eBook-Downloader/master/version').data
    newest_version = ver.decode('ascii')[:-1].split('_', 2)
    for i in range(0, 3):
        if VERSION[i] < newest_version[i]:
            print()
            print("!!! UPDATE AVAILABLE !!!")
            print("https://github.com/IceflowRE/MR-eBook-Downloader/releases/latest")
            print()
            break
    https.clear()


def delete_dir_rec(path):
    """
    Deletes a folder recursive.
    :return:
    """
    for sub in path.iterdir():
        if sub.is_dir():
            delete_dir_rec(sub)
        else:
            sub.unlink()
    path.rmdir()


def clean_up():
    """
    Deletes temp folder.
    :return:
    """
    print('== DELETE TEMP ==')

    if temp_path.exists():
        delete_dir_rec(temp_path)
    if temp_path.exists():
        print('::ERROR:: Temporary file was not deleted successful.')


def create_needed_files():
    """
    Create all needed files.
    :return:
    """
    if not threads_path.exists():  # create temp and threads path
        Path.mkdir(threads_path, parents=True)
    if not download_path.exists():
        Path.mkdir(download_path)
    if not update_config_path.exists():
        with update_config_path.open(mode='w', encoding="utf8") as writer:
            writer.write('{}')


def load_from_jsonfile():
    """
    Loads the already downloaded ebooks.
    :return:
    """
    print("== LOAD EBOOK UPDATE FILE ==")

    global ebook_link_dict_old

    with update_config_path.open(mode='r', encoding="utf8") as data_file:
        ebook_link_dict_old = json.loads(data_file.read())

    if 'wikilist_date' not in ebook_link_dict_old.keys():
        ebook_link_dict_old['wikilist_date'] = 0

    for item in ebook_link_dict_old:
        if not item.isdigit() and (item is not None):
            attach_id = re.search(r"attachmentid=(\d)*", item)
            if attach_id is not None:
                attach_id = attach_id.group()[13:]
                ebook_link_dict_old[attach_id] = ebook_link_dict_old.pop(item)


def download_ebook_list():
    """
    Downloads the main page html with ebook list.
    :return:
    """
    print('== DOWNLOAD EBOOK LIST ==')

    https = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    with https.request('GET', 'https://wiki.mobileread.com/wiki/Free_eBooks-de/de', preload_content=False,
                       retries=urllib3.util.retry.Retry(3)) as load:
        with temp_path.joinpath('main_list.html').open(mode='wb') as out_file:
            out_file.write(load.data)
    https.clear()


def get_ebook_threads():
    """
    Extracts the ebook threads from the wiki list.
    :return:
    """
    print('== EXTRACT THREADS LINKS ==')

    global thread_list
    global ebook_link_dict

    parser = ListHTMLParser.ListHTMLParser(format_list)
    with temp_path.joinpath('main_list.html').open(mode='r', encoding="utf8") as reader:
        parser.feed(reader.read())
    parser.close()

    thread_list = parser.thread_list
    ebook_link_dict['wikilist_date'] = parser.wiki_list_date

    if ebook_link_dict['wikilist_date'] == 0:
        print("::ERROR:: Something wents wrong the wikilist time is 0")
        sys.exit()
    if ebook_link_dict['wikilist_date'] == ebook_link_dict_old['wikilist_date']:
        print("Since last download nothing changed. No update is required.")
        sys.exit()

    print('Threads found: ' + str(len(thread_list)))


def download_html_as_file(url, target_path: Path):
    """
    Downloads the given files to the goven target path.
    :param url: URL.
    :param target_path: the target file.
    :return:
    """
    download_success = "TRUE"

    try:
        while target_path.exists():
            target_path = Path(str(target_path) + "_d")

        with downloader.request('GET', url, preload_content=False, retries=urllib3.util.retry.Retry(3)) as reader:
            if reader.status == 200:
                with target_path.open(mode='wb') as out_file:
                    out_file.write(reader.data)
            else:
                raise urllib3.exceptions.HTTPError(str(reader.status))
    except Exception as exception:
        download_success = "DOWNLOAD ERROR " + str(exception) + ": " + url

    return download_success


def reset_progress():
    """
    Resets the progress bar to 0.
    :return:
    """
    global done_links
    done_links = 0


def print_progress(full_percentage, job):
    """
    Callback function prints a progress bar.
    :param full_percentage: The number which is 100%.
    :param job: The multi processing job result.
    :return:
    """
    global done_links
    done_links += 1
    if full_percentage != 0:
        print('\r' + 'Progress: %d/%d  |  %d %%' % (
            done_links, full_percentage, round((100 / full_percentage * done_links), 1)), end='')
    else:
        print('\r' + 'Error for full_percentage....', end='')


def download_ebook_threads():
    """
    Download the extracted threads.
    :return:
    """
    print('== DOWNLOAD EBOOK THREADS ==')

    reset_progress()

    with futures.ProcessPoolExecutor(max_workers=using_cores) as executor:
        for link in thread_list:
            # remove invalid file chars from file name
            thread_name = link.replace('?', '_').replace('/', '%') + '.html'

            job = executor.submit(download_html_as_file, link, threads_path.joinpath(thread_name))
            job.add_done_callback(functools.partial(print_progress, len(thread_list)))
    print()


def exist_thread(thread):
    """
    Checks if an thread exist as html in temp/threads.
    :param thread:
    :return:
    """
    path = threads_path.joinpath(thread.replace('?', '_').replace('/', '%') + '.html')
    if not path.is_file():
        print("Thread " + thread + " was not downloaded.")
        return False
    return True


def check_downloaded_threads():
    """
    Check for not downloaded threads and removes them from the thread list too.
    :return:
    """
    global thread_list

    thread_list = [thread for thread in thread_list if exist_thread(thread)]  # list contains only existing threads


def get_ebook_links_from_file(path: Path):
    """
    Extracts the ebook attachment links from given file.
    :param path:
    :return:
    """
    parser = ThreadHTMLParser.ThreadHTMLParser(path)
    try:
        with path.open(mode='r', encoding="utf-8") as reader:
            parser.feed(reader.read())
    except Exception:
        return [], path
    not_found = ''
    thread_ebook_dict = {}
    for item in parser.link_data_list:
        valid_name = re.sub('[^\w\-_. ]', '_', item[1])
        thread_ebook_dict[item[0]] = (valid_name, parser.time)
    if len(thread_ebook_dict) <= 0:
        not_found = path
    return thread_ebook_dict, not_found


def collect_ebook_list(job):
    """
    Callback function collects and puts all ebook links together.
    :param job: (thread_ebook_dict <dict>, not_found <dict>)
    :return:
    """
    global ebook_link_dict
    global not_found_ebooks_thread
    try:
        result = job.result()
    except Exception as exception:
        print(str(exception))
        return

    if len(result[1]) == 0:
        ebook_link_dict = {**ebook_link_dict, **result[0]}
    else:
        not_found_ebooks_thread.append(result[1])


def get_ebook_links():
    """
    The main methode which get all ebook links with multi processing.
    :return:
    """
    print('== GET EBOOK LINKS ==')

    if len(thread_list) == 0:
        print("No thread download was successful.")
        sys.exit()

    reset_progress()

    with futures.ProcessPoolExecutor(max_workers=using_cores) as executor:
        for link in thread_list:  # all thread htmls
            # remove invalid file chars from file name
            thread_name = link.replace('?', '_').replace('/', '%') + '.html'

            job = executor.submit(get_ebook_links_from_file, threads_path.joinpath(thread_name))
            job.add_done_callback(functools.partial(print_progress, len(thread_list)))
            job.add_done_callback(collect_ebook_list)

    print()
    print('eBooks found: ' + str(len(ebook_link_dict) - 1))  # -1 due to wikilist date
    print('Nothing found in !' + str(len(not_found_ebooks_thread)) + "! threads")
    # for item in not_found_ebooks_thread:  # debug proposes
    #     print(item)  # debug proposes


def check_for_updates():
    """
    Extracts the new, needed ebook links from the already downloaded files.
    :return:
    """
    print("== GENERATE DONWLOAD LIST ==")

    for at_id, value in ebook_link_dict.items():
        if at_id == 'wikilist_date':  # exclude the wikilist date
            continue
        if at_id in ebook_link_dict_old:  # if the ebook already was downloaded
            if value[1] > ebook_link_dict_old[at_id][1]:  # if edited time is newer
                ebook_download_list.append(at_id)
        else:
            ebook_download_list.append(at_id)

    # http://stackoverflow.com/questions/20672238/find-dictionary-keys-with-duplicate-values
    # exists more then one time on the ebook lists
    rev_multidict = {}
    for key, value in ebook_link_dict.items():
        rev_multidict.setdefault(value, set()).add(key)
    print("Duplicates: " + str([key for key, values in rev_multidict.items() if len(values) > 1]))

    print("eBooks to download: " + str(len(ebook_download_list)))


def ebook_download_succeed(at_id, job):
    """
    Callback function for checking if the download was succeed.
    ONLY for ebook downloading!
    :param at_id:
    :param job:
    :return:
    """
    global download_succeed_list
    global download_failed_list

    try:
        result = job.result()
    except Exception:
        download_failed_list.append(at_id)
        return

    if result == "TRUE":
        name = ebook_link_dict[at_id][0]
        filename = download_path.joinpath(name[:name.rfind('.')] + '_id' + at_id + name[(name.rfind('.') - len(name)):])
        with filename.open(mode='r', encoding="utf-8") as reader:
            check = reader.readline(14)
            if check == "<!DOCTYPE html":  # if only the html file "Invalid Attachment specified." was downloaded
                download_failed_list.append(at_id)
            else:
                download_succeed_list.append(at_id)
    else:
        # print(result) # prints error message; debug proposes
        download_failed_list.append(at_id)


def download_ebooks():
    """
    Main methode for downloading the ebooks with multi processing.
    :return:
    """
    print("== DOWNLOAD EBOOKS ==")

    reset_progress()
    with futures.ProcessPoolExecutor(max_workers=using_cores) as executor:
        for at_id in ebook_download_list:
            name = ebook_link_dict[at_id][0]
            file_name = name[:name.rfind('.')] + '_id' + at_id + name[(name.rfind('.') - len(name)):]
            job = executor.submit(download_html_as_file, '/forums/attachment.php?attachmentid=' + at_id,
                                  download_path.joinpath(file_name))
            job.add_done_callback(functools.partial(print_progress, len(ebook_download_list)))
            job.add_done_callback(functools.partial(ebook_download_succeed, at_id))
    print()
    print(str(len(download_succeed_list)) + "/" + str(len(ebook_download_list)) + " downloads succeed.")


def update_jsonfile():
    """
    Updates the already downloaded ebook update file.
    :return:
    """
    print("== UPDATE EBOOK UPDATE FILE ==")

    global ebook_link_dict_old

    ebook_link_dict_old['wikilist_date'] = ebook_link_dict['wikilist_date']
    for link in download_succeed_list:
        ebook_link_dict_old[link] = ebook_link_dict[link]

    jsondata = json.dumps(ebook_link_dict_old, indent=4, sort_keys=True)
    with update_config_path.open(mode='w', encoding="utf8") as writer:
        writer.write(jsondata)


def write_no_ebook_founds():
    """
    More a debug function, writes all forum threads which are on the wiki list and do not contain an ebook.
    :return:
    """
    with Path("./noEbookFound.txt").open(mode='w', encoding="utf8") as writer:
        for item in not_found_ebooks_thread:
            writer.write('http://www.mobileread.com' + item[15:-5].replace('_', '?').replace('%', '/') + '\n')


def write_failed_downloads():
    """
    Writes the failed downloads to a file.
    :return:
    """
    with Path("downloadFailed.txt").open(mode='w', encoding="utf8") as writer:
        for at_id in download_failed_list:
            writer.write(ebook_link_dict[at_id][0] + "\t" + "/forums/attachment.php?attachmentid=" + at_id + '\n')


def close_downloader():
    """
    Closes the downloader.
    :return:
    """
    downloader.close()
