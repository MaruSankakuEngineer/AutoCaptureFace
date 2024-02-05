import yaml


def load_yaml(yaml_path: str) -> dict:
    """
    yamlファイルを読み込む

    Args:
        yaml_path (str): 読み込むyamlファイルのパス

    Returns:
        dict: 読み込んだデータ
    """
    with open(yaml_path, "r") as f:
        load_data = yaml.safe_load(f)
    return load_data

def dump_yaml(yaml_path: str, dump_data: dict):
    """
    yamlにデータを書き込む

    Args:
        yaml_path (str): 書き込み先yamlのパス
        dump_data (dict): yamlに書き込むデータ
    """
    with open(yaml_path, "w") as f:
        yaml.dump(dump_data, f, default_flow_style=False)
