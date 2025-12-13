## Setup

Raycastの設定画面を開き、Extensions -> Scripts -> Add Script Directory で適当なフォルダを指定し、そこに`raycast.sh`を配置します。


```sh
# 自分用のmake command。環境によるので自分で確認してください。
$ make cp-raycast-script
```

## Troubleshooting

#### macOS

1. システム設定 を開く。
2. プライバシーとセキュリティ -> アクセシビリティ を開く。
   1. Raycast が ON になっているか確認。
3. プライバシーとセキュリティ -> オートメーション を開く。
   1. Raycast の項目を展開し、System Events が ON になっているか確認。