import os
import sys
import shutil
import functools
import json
import re
from concurrent import futures
import certifi
import urllib3
import ListHTMLParser
import ThreadHTMLParser
# import multiprocessing

VERSION = ['1', '1', '0']

temp_path = './temp/'
threads_path = './temp/threads/'
download_path = './ebooks/'
update_config_path = "update.data"
using_cores = 4  # multiprocessing.cpu_count()

downloader = urllib3.HTTPConnectionPool('www.mobileread.com', maxsize=using_cores)
format_list = ['epub', 'mobi', 'lrf', 'imp', 'pdf', 'lit', 'azw', 'azw3', 'rar', 'lrx']
thread_list = []
ebook_link_dict = {}  # (link, [name, time])
ebook_link_dict_old = {}
ebook_download_list = []
download_succeed_dict = {}
not_found_ebooks_thread = []
done_links = 0


def init():
    """
    Initializes the needed global variables to proceed the installation.
    :return:
    """
    print('== INITIALIZE APPLICATION ==')

    if sys.version_info <= (3, 0):
        sys.exit('Only Python 3.0 or greater is supported. You are using:' + str(sys.version_info))

    ebook_link_dict['wikilist_date'] = 0


def check_for_app_updates():
    print("== CHECK FOR APPLICATION UPDATES ==")

    https = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    ver = https.urlopen('GET', 'https://raw.githubusercontent.com/IceflowRE/MR-eBook-Downloader/master/version').data
    newest_version = ver.decode('ascii')[:-1].split('_', 2)
    for i in range(0, 3):
        if VERSION[i] < newest_version[i]:
            print()
            print("!!! NEW VERSION AVAILABLE !!!")
            print("https://github.com/IceflowRE/MR-eBook-Downloader/releases/latest")
            print()


def clean_up():
    """
    Deletes temp folder.
    :return:
    """
    print('== DELETE TEMP ==')

    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


def create_needed_files():
    """
    Create all needed files.
    :return:
    """
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    if not os.path.exists(threads_path):
        os.makedirs(threads_path)
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    if not os.path.isfile(update_config_path):
        with open(update_config_path, 'w') as writer:
            writer.write('{}')
        writer.close()


def load_from_jsonfile():
    """
    Loads the already downloaded ebooks.
    :return:
    """
    print("== LOAD EBOOK UPDATE FILE ==")

    global ebook_link_dict_old
    ebook_link_dict_old['wikilist_date'] = 0
    with open(update_config_path) as data_file:
        ebook_link_dict_old = json.loads(data_file.read())

    if 'wikilist_date' not in ebook_link_dict_old:
        ebook_link_dict_old['wikilist_date'] = 0


def download_ebook_list():
    """
    Downloads the main page html with ebook list.
    :return:
    """
    print('== DOWNLOAD EBOOK LIST ==')

    http = urllib3.PoolManager()

    with http.request('GET', 'http://wiki.mobileread.com/wiki/Free_eBooks-de/de', preload_content=False) as load, open(
            (temp_path + 'main_list.html'), 'wb') as out_file:
        shutil.copyfileobj(load, out_file)
    load.release_conn()


def get_ebook_threads():
    """
    Extracts the ebook threads from the wiki list.
    :return:
    """
    print('== EXTRACT THREADS LINKS ==')

    global thread_list
    global ebook_link_dict

    parser = ListHTMLParser.ListHTMLParser(format_list)
    parser.feed(open(temp_path + 'main_list.html', encoding="utf8").read())
    parser.close()

    thread_list = parser.thread_list
    ebook_link_dict['wikilist_date'] = parser.wiki_list_date

    if ebook_link_dict['wikilist_date'] == 0:  # Debug
        print("::ERROR:: Something wents wrong the wikilist time is 0")
    if ebook_link_dict['wikilist_date'] == ebook_link_dict_old['wikilist_date']:
        print("Since last download nothing changed. No update is required.")
        sys.exit()

    print('Threads found: ' + str(len(thread_list)))


def download_html_as_file(url, target_path):
    """
    Downloads the given files to the goven target path.
    :param url: URL.
    :param target_path: the target file.
    :return:
    """
    try:
        while os.path.isfile(target_path):
            target_path += "_d"
        with downloader.request('GET', url, preload_content=False) as reader, open(str(target_path), 'wb') as out_file:
            shutil.copyfileobj(reader, out_file)
        reader.release_conn()
    except Exception as exception:
        print("DOWNLOAD ERROR: " + url + " MSG: " + str(exception))
        return False
    return True


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

            job = executor.submit(download_html_as_file, link, (threads_path + thread_name))
            job.add_done_callback(functools.partial(print_progress, len(thread_list)))
    print()


def get_ebook_links_from_file(path):
    """
    Extracts the ebook attachment links from given file.
    :param path:
    :return:
    """
    parser = ThreadHTMLParser.ThreadHTMLParser(path)
    try:
        parser.feed(open(path, encoding="latin-1").read())
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
    :param job:
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

    reset_progress()

    with futures.ProcessPoolExecutor(max_workers=using_cores) as executor:
        for link in thread_list:  # all thread htmls
            # remove invalid file chars from file name
            thread_name = link.replace('?', '_').replace('/', '%') + '.html'

            job = executor.submit(get_ebook_links_from_file, (threads_path + thread_name))
            job.add_done_callback(functools.partial(print_progress, len(thread_list)))
            job.add_done_callback(collect_ebook_list)

    print()
    print('eBooks found: ' + str(len(ebook_link_dict)))
    print('Nothing found in !' + str(len(not_found_ebooks_thread)) + "! threads")
    # for item in not_found_ebooks_thread:  # debug proposes
    #     print(item)  # debug proposes


def check_for_updates():
    """
    Extracts the new, needed ebook links from the already downloaded files.
    :return:
    """
    print("== GENERATE DONWLOAD LIST ==")

    for key, value in ebook_link_dict.items():
        if key == 'wikilist_date':  # exclude the wikilist date
            continue
        if key in ebook_link_dict_old:
            if value[1] > ebook_link_dict_old[key][1]:
                ebook_download_list.append((key, value[0]))
        else:
            ebook_download_list.append((key, value[0]))

    rev_multidict = {}
    for key, value in ebook_link_dict.items():
        rev_multidict.setdefault(value, set()).add(key)
    print("Duplicates: " + str([key for key, values in rev_multidict.items() if len(values) > 1]))

    print("eBooks to download: " + str(len(ebook_download_list)))


def ebook_download_succeed(link, job):
    """
    Callback function for checking if the download was succeed.
    :param link:
    :param job:
    :return:
    """
    try:
        result = job.result()
    except Exception:
        print("  Failed to download: " + link)
        return

    if result:
        download_succeed_dict[link] = ebook_link_dict[link]
    else:
        print("  Failed to download: " + link)


def download_ebooks():
    """
    Main methode for downloading the ebooks with multi processing.
    :return:
    """
    print("== DOWNLOAD EBOOKS ==")

    reset_progress()

    with futures.ProcessPoolExecutor(max_workers=using_cores) as executor:
        for item in ebook_download_list:
            attach_id = re.search(r"attachmentid=(\d)*", item[0])
            if attach_id is not None:
                attach_id = attach_id.group()[13:]
            else:
                attach_id = ''
            file_name = item[1][:item[1].rfind('.')] + '_id' + attach_id + item[1][(item[1].rfind('.') - len(item[1])):]
            job = executor.submit(download_html_as_file, '/forums/' + item[0], download_path + file_name)
            job.add_done_callback(functools.partial(print_progress, len(ebook_download_list)))
            job.add_done_callback(functools.partial(ebook_download_succeed, item[0]))
    print()


def update_jsonfile():
    """
    Updates the already downloaded ebook update file.
    :return:
    """
    print("== UPDATE EBOOK UPDATE FILE ==")

    global ebook_link_dict_old

    download_succeed_dict['wikilist_date'] = ebook_link_dict['wikilist_date']
    ebook_link_dict_old = {**ebook_link_dict_old, **download_succeed_dict}

    jsondata = json.dumps(ebook_link_dict_old, indent=4, sort_keys=True)
    with open(update_config_path, 'w') as writer:
        writer.write(jsondata)
    writer.close()


def write_no_ebook_founds():
    """
    More a debug function, writes all forum threads which are on the wiki list and do not contain an ebook.
    :return:
    """
    with open("noEbookFound.txt", 'w') as writer:
        for item in not_found_ebooks_thread:
            writer.write('http://www.mobileread.com' + item[15:-5].replace('_', '?').replace('%', '/') + '\n')
    writer.close()


def close_downloader():
    """
    Closes the downloader.
    :return:
    """
    downloader.close()
