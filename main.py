import os
import requests
from tqdm import tqdm
import re


def API_Call(max_cursor, uid):
    API_ENDPOINT = f"https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid={uid}&count=10&max_cursor={max_cursor}"
    headers = {
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/95.0.4638.84 Safari/537.36 '
    }
    data = requests.get(API_ENDPOINT, headers=headers)
    return data.json()


def get_data(uid, max_cursor):
    data = []
    data_json = API_Call(uid=uid, max_cursor=max_cursor)
    if data_json and "aweme_list" in data_json.keys():
        aweme_list = data_json["aweme_list"]
        for item in aweme_list:
            src = item["video"]["play_addr"]["url_list"][-1]
            desc = item["desc"]
            aweme_id = item["aweme_id"]
            data.append({
                "id": aweme_id,
                "src": src,
                "desc": desc
            })
    if data_json["has_more"]:
        return data, data_json['max_cursor']
    else:
        return data, None


def download(url, aweme_id, desc):
    file_name = aweme_id + "-" + desc + ".mp4"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/95.0.4638.84 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
    }
    response = requests.get(url=url, headers=headers, stream=True, timeout=10000)
    content_size = int(int(response.headers['Content-Length']) / 1024)
    with open(f'Download/{file_name}', "wb") as f:
        print("Total Size: ", content_size, 'k,start...')
        for data in tqdm(iterable=response.iter_content(1024), total=content_size, unit='k', desc=file_name[:19]):
            f.write(data)
        print(file_name[:19], "download finished!")


def main(link):
    """
    :param link: Uid of user (https://www.douyin.com/user/MS4wLjABAAAAM83vEaMRlBIjnJhbDrujETyATNE159vPeYbPr7IXQzA)
    """

    url = "https://www.douyin.com/user/"
    uid = re.split(url, link)[-1]
    max_cursor = 0
    all_data = []
    while True:
        data, max_cursor = get_data(uid=uid, max_cursor=max_cursor)
        all_data += data
        if not max_cursor:
            break
    for item in all_data:
        try:
            download(url=item["src"], aweme_id=item["id"], desc=item["desc"])
        except Exception as e:
            with open('error.log', 'a', encoding='utf-8') as f:
                f.write('error at' + item['src'] + str(e) + '\n')
                f.close()


if __name__ == "__main__":
    try:
        os.makedirs("Download")
    except FileExistsError:
        print("exists")
    main("https://www.douyin.com/user/MS4wLjABAAAAM83vEaMRlBIjnJhbDrujETyATNE159vPeYbPr7IXQzA")
