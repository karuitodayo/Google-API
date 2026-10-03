"""
Google Meet API (v2) を使って「新しいGoogle Meetの会議室（スペース）」を作成するスクリプト

【Google Meet APIについて】
このAPIは、Calendarの予定とは関係なく、「今すぐ使える会議室リンク」だけを
その場で1つ発行するためのAPI。日時やタイトルの概念はなく、
「会議室を1つ作る」というシンプルな操作のみを行う。

事前準備:
1. Google Cloud Console で「Google Meet API」を有効化する
   (APIとサービス > ライブラリ > "Google Meet API" を検索して有効化)
2. OAuth同意画面の「テストユーザー」に自分のGoogleアカウントが
   追加されていることを確認する（Docsの課題で設定済みのはず）
3. Google Cloud Console で作成した OAuth クライアントID（デスクトップアプリ）の
   JSONファイルを "client_secret.json" としてこのフォルダに置く
   （今回は AI学習 フォルダ直下にあったものをコピー済み）
4. pip install -r requirements.txt
"""

import os

# ブラウザでのログイン許可（OAuth認証）を行うためのライブラリ
from google_auth_oauthlib.flow import InstalledAppFlow

# 一度ログインして得た認証情報を、ファイルに保存・読み込みするためのライブラリ
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Google の各種API（Meet など）を呼び出すためのライブラリ
from googleapiclient.discovery import build

# ---------------------------------------------------------------------------
# 設定
# ---------------------------------------------------------------------------

# OAuthクライアントの設定ファイル（Cloud Consoleでダウンロードしたもの）
CLIENT_SECRET_FILE = "client_secret.json"

# ログイン情報（アクセストークン）を保存しておくファイル
# スコープがDocs/Driveの課題と異なるため、token.jsonはこのフォルダ専用にする
TOKEN_FILE = "token.json"

# このプログラムがGoogleに対して「何をしたいか」を宣言するもの（スコープ＝権限の範囲）
# 「自分が作成した会議室の作成・参照」ができる最小限の権限
SCOPES = ["https://www.googleapis.com/auth/meetings.space.created"]


# ---------------------------------------------------------------------------
# 処理の本体
# ---------------------------------------------------------------------------

def get_credentials() -> Credentials:
    """OAuth認証を行い、Meet APIを呼び出すための認証情報を取得する"""
    creds = None

    # 以前ログイン済みで、token.json が残っていればそれを読み込む
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # 有効な認証情報がない場合（初回、または期限切れの場合）
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # 期限切れだが refresh_token があれば、再ログインなしで更新できる
            creds.refresh(Request())
        else:
            # 初回はブラウザを開いてログイン・許可を行ってもらう
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # 次回から使えるように、認証情報をファイルに保存しておく
        with open(TOKEN_FILE, "w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())

    return creds


def create_meet_space(meet_service, access_type: str | None = None) -> dict:
    """新しいMeetの会議室（スペース）を1つ作成し、その情報を返す

    access_type: "OPEN" / "TRUSTED" / "RESTRICTED" のいずれか。
                 None の場合は省略し、Googleのデフォルト設定に任せる。
    """
    body = {}
    if access_type:
        # config.accessType で「承認なしで参加できる範囲」を指定する
        body["config"] = {"accessType": access_type}

    space = meet_service.spaces().create(body=body).execute()
    return space


def main():
    # 1. OAuth認証を行い、Meet APIを呼び出す準備をする（初回はブラウザが開く）
    creds = get_credentials()
    meet_service = build("meet", "v2", credentials=creds)

    # 2. 会議室（スペース）を新規作成する（今回は accessType を明示的に指定してみる）
    space = create_meet_space(meet_service, access_type="TRUSTED")

    # 3. 結果を表示する
    print("会議室を作成しました。")
    print(f"参加用リンク: {space['meetingUri']}")
    print(f"会議コード: {space['meetingCode']}")
    print(f"リソース名: {space['name']}")
    print(f"設定(config): {space.get('config')}")


if __name__ == "__main__":
    main()
