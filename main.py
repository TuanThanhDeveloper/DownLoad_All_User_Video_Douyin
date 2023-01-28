import os
import requests
from tqdm import tqdm
import re


def API_Call(max_cursor, uid):
    # https://www.iesdouyin.com/aweme/v1/web/aweme/detail/?aweme_id=7117197143789587743
    # https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={key}
    # https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid={uid}
    API_ENDPOINT = f"https://www.iesdouyin.com/web/api/v2/aweme/post/?sec_uid={uid}&count=10&max_cursor={max_cursor}"
    headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'cookie': 'ttwid=1%7C3HbML7q9_eeKsEofw6GPkCQJKujXwEo4XHGHcuEsTuo%7C1671954699%7C9285b746d8b5071e685222150c7a84b33cbb70361a82ea0c8b2d1b3a4423b6db; s_v_web_id=verify_lc32nrh9_XsMyWHWX_O8q3_4kuO_BoIj_Jors6W0Ums9b; _tea_utm_cache_1243={%22utm_source%22:%22copy_link%22%2C%22utm_medium%22:%22android%22%2C%22utm_campaign%22:%22client_share%22}; tt_scid=GTPZykJ.6PwFXZiqmGWouaq8TrMM9yPwIuHxlaYmVED8IZ5Nlec2LTBPVpK0Rlwj26fb; msToken=jK3WGwRCGIePXzfI0M47BHwB-pEQyuMzWL2MSoj42C2rprW-g4Ro_I2V_9yepGWbpnwh2zgUnSSIFQEFvw761QmJjPI-Gojh5UKQGUSLzf6xYCdvn-eYOscNiZSXSyM=; _tea_utm_cache_2018={%22utm_source%22:%22copy_link%22%2C%22utm_medium%22:%22android%22%2C%22utm_campaign%22:%22client_share%22}; __ac_nonce=063d4a54300ceeb4c1666; __ac_signature=_02B4Z6wo00f01HvYPyQAAIDBWHkRibAwVlx7.DuAAH0qeSrJLgmnnLDV-MXCsbAwZR1Njuygts0EHfaLhHEB0pRDzjedyZ8JGwhBIFcrP2FWmBjvm-GVyA5svZbmaoDONk2d9TnLne73TM9N7e; __ac_referer=https://www.iesdouyin.com/share/video/7117197143789587743/?region=VN&mid=6809932063278402307&u_code=0&did=MS4wLjABAAAAc3XddZLLY6UIsmK8D_yZY484QYB9-UUdt9RvPl9_pvk&iid=MS4wLjABAAAAFE0EVq4kaQnT1DhZPaKp7spOYru9qVEaJt-25OEEDmhd7WwxUAkvwLfEiGLlr52M&with_sec_did=1&titleType=title&utm_source=copy_link&utm_campaign=client_share&utm_medium=android&app=aweme; msToken=GUrVNhPRSAet1cbWXTjNaWYYqm0s2jAc0OVvD28ep7E2SzsBEuuacWQhNk9pdQhyNwX0nzk8N9Onmp8lRyldG-wk6PEByT4XQ0t05rgQqh-UGB3JIDKh43aCIATP8fg='
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
    main('https://www.douyin.com/user/MS4wLjABAAAAQTAK0xJUnVyLDIp38HBkAGkRPECaVHmKZE5d2MMywek')
