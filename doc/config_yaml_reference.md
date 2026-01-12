# config.yaml 設定リファレンス

本ドキュメントは、本リポジトリで使用する `config.yaml` の各設定項目について、
目的・設定可能な値・設定による挙動の違い・出力されるログファイルを説明する。

本ツールは **EDR 製品そのものではなく**、  
EDR が持つ代表的な「基礎動作」を **負荷・挙動観点でシミュレーション**することを目的としている。

## 本設定ファイルの位置づけ

* 実運用 EDR の設定を再現するものではない
* **負荷傾向・挙動理解のための実験用設定**
* 検証環境・目的に応じて意図的に「過激な設定」を行うことを想定



## 設計方針（前提）

- 特定の EDR 製品名・ベンダー実装を模倣しない
- 「何をすると、どのリソースが使われるか」を観察可能にする
- 再現度よりも **負荷傾向・挙動理解**を優先する


## config.yaml 全体構成例

```yaml
packet_inspection:
  enable: true
  mode: mock
  burst:
    size: 1000
    interval_ms: 10

logging:
  base_dir: ./logs
````


## packet_inspection セクション

パケット監視・解析処理を模した機能に関する設定。

### packet_inspection.enable

| 項目    | 内容                 |
| ----- | ------------------ |
| 型     | boolean            |
| デフォルト | false              |
| 説明    | パケット監視処理を有効化するかどうか |

#### 設定例

```yaml
packet_inspection:
  enable: true
```

#### 挙動

* `true` の場合、packet_inspection 処理スレッドが起動する
* `false` の場合、packet_inspection に関する処理・ログは一切出力されない


### packet_inspection.mode

| 項目    | 内容               |
| ----- | ---------------- |
| 型     | string           |
| 設定可能値 | `mock`, `pcap`   |
| デフォルト | mock             |
| 説明    | パケット取得・解析方法を指定する |

#### 各 mode の意味

| mode | 内容                             |
| ---- | ------------------------------ |
| mock | 疑似パケットを生成し、CPU負荷を中心とした挙動を再現    |
| pcap | pcap ファイルを入力としたパケット解析（※将来拡張予定） |

#### 重要な注意点

* `mock` モードでは **実際のパケット取得・解析は行わない**
* `mock` モードでは **パケット内容を記録するログは出力されない**
* `pcap` モードは現時点では設計のみで、実装は未完了


### packet_inspection.burst

短時間に集中的な処理（バースト）を発生させるための設定。

#### burst.size

| 項目   | 内容                   |
| ---- | -------------------- |
| 型    | integer              |
| 設定範囲 | 1 ～ 数万（環境依存）         |
| 説明   | 1バーストあたりに処理する疑似パケット数 |

#### burst.interval_ms

| 項目   | 内容               |
| ---- | ---------------- |
| 型    | integer          |
| 設定範囲 | 1 ～              |
| 説明   | バースト処理の実行間隔（ミリ秒） |

#### 設定例（CPU 高負荷）

```yaml
packet_inspection:
  enable: true
  mode: mock
  burst:
    size: 5000
    interval_ms: 1
```

#### 挙動

* CPU 使用率が急激に上昇し、環境によっては 100% に張り付く
* 処理はメモリ上で完結するため、ディスク IO はほぼ発生しない



## logging セクション

ログ出力に関する共通設定。

### logging.base_dir

| 項目    | 内容               |
| ----- | ---------------- |
| 型     | string           |
| デフォルト | ./logs           |
| 説明    | ログファイルの出力先ディレクトリ |



### logging.level

| 項目    | 内容                                  |
| ----- | ----------------------------------- |
| 型     | string                              |
| 設定可能値 | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| デフォルト | INFO                                |
| 説明    | ログ出力レベル                             |



## 出力されるログファイル一覧

### mock モード時

| ログファイル名                     | 出力有無 | 説明                    |
| --------------------------- | ---- | --------------------- |
| edr-main.log                | ○    | 起動・設定読み込み・スレッド開始/終了ログ |
| edr-mock_packet_watcher.log | ×    | mock モードでは出力されない（仕様）  |

#### 補足

`mock` モードは **負荷生成専用モード**であり、
パケット内容・イベント詳細を記録することを目的としていない。

---

# config.yaml 設定項目サポートマトリクス

本ドキュメントでは、`config.yaml` に定義されている各設定項目について、

- **現在の実装で実際に使用されている項目**
- **設定項目として存在するが未使用のもの**
- **設計上は意図されており将来実装予定のもの**

を明確に整理する。

本プロジェクトは「EDR の挙動・負荷特性を理解するためのシミュレーター」であり、
すべての設定項目が現時点で有効とは限らない点に注意すること。



## 1. edr セクション

```yaml
edr:
  name: edr-mock
  mode: behavior_based
````

| パラメータ    | サポート状況 | 説明        |
| -------- | ------ | --------- |
| edr.name | ❌ 未使用  | 現状はメタ情報のみ |
| edr.mode | ❌ 未使用  | 動作分岐は未実装  |

**補足**
将来的にログヘッダや挙動分岐（signature_based / behavior_based 等）へ反映可能。

---

## 2. file_inspection セクション

```yaml
file_inspection:
  enable: true
  paths:
  recursive: true
  min_size_kb: 4
  max_size_mb: 10
  inspect_extensions: [...]
  light_scan_hash_loops: 200
  full_scan_hash_loops: 1000
  burst_control: ...
```

### サポート状況

| パラメータ                    | サポート状況 | 備考                |
| ------------------------ | ------ | ----------------- |
| enable                   | ✅ 使用中  | file_watcher 起動制御 |
| paths                    | ✅ 使用中  | 監視ディレクトリ          |
| recursive                | ⚠ 一部   | watchdog 設定依存     |
| min_size_kb              | ❌ 未使用  | 条件分岐未実装           |
| max_size_mb              | ❌ 未使用  | 条件分岐未実装           |
| inspect_extensions       | ❌ 未使用  | 拡張子フィルタ未実装        |
| light_scan_hash_loops    | ✅ 使用中  | 軽量スキャン負荷          |
| full_scan_hash_loops     | ✅ 使用中  | フルスキャン負荷          |
| burst_control.threshold  | ✅ 使用中  | バースト検知            |
| burst_control.window_sec | ✅ 使用中  | バースト窓             |
| burst_control.delay_ms   | ✅ 使用中  | スロットリング           |

### 実際の挙動

* ファイルイベント検知時に **hash loop による CPU 負荷を生成**
* サイズ・拡張子条件は **現時点では未反映**
* light / full スキャンの切替条件は **コード側ロジック**

---

## 3. packet_inspection セクション

```yaml
packet_inspection:
  enable: true
  mode: mock
  interface: null
  protocols: [...]
  ports: ...
  payload_inspection: ...
  burst_control: ...
```

### サポート状況

| パラメータ                     | サポート状況 | 備考                  |
| ------------------------- | ------ | ------------------- |
| enable                    | ✅ 使用中  | packet_watcher 起動制御 |
| mode                      | ⚠ 部分   | mock のみ有効           |
| interface                 | ❌ 未使用  | pcap 用              |
| protocols                 | ❌ 未使用  | 未実装                 |
| ports.include             | ❌ 未使用  | 未実装                 |
| ports.exclude             | ❌ 未使用  | 未実装                 |
| payload_inspection.enable | ❌ 未使用  | 構造定義のみ              |
| min_payload_size          | ❌ 未使用  | 未実装                 |
| hash_loops                | ✅ 使用中  | mock 負荷生成           |
| burst_control.*           | ✅ 使用中  | バースト制御              |

### mode 別の注意点

#### mock モード（現在）

* 疑似パケット生成による **CPU 負荷再現**
* 実パケットは扱わない
* `edr-mock_packet_watcher.log` は基本的に出力されない

#### pcap モード（将来）

* pcap ファイルまたは NIC から取得
* protocol / port / payload フィルタ有効化
* 実通信に近い検証が可能

---

## 4. logging セクション

```yaml
logging:
  base_dir: logs
  default:
  components:
```

### サポート状況

| パラメータ               | サポート状況 | 備考             |
| ------------------- | ------ | -------------- |
| base_dir            | ✅ 使用中  | ログ出力先          |
| default.level       | ✅ 使用中  | デフォルトログレベル     |
| default.file        | ✅ 使用中  | メインログ          |
| timestamp           | ✅ 使用中  | JSON ts        |
| rotation.type=size  | ✅ 使用中  | サイズローテーション     |
| rotation.type=daily | ⚠ 定義のみ | 未完全対応          |
| rotation.type=none  | ⚠ 定義のみ | 未検証            |
| components.*.level  | ✅ 使用中  | component 単位制御 |

---

## 5. metrics 系 component

```yaml
components:
  metrics:
  metrics_debug:
```

| パラメータ         | サポート状況 | 説明         |
| ------------- | ------ | ---------- |
| metrics       | ✅ 使用中  | CPU / メモリ  |
| metrics_debug | ⚠ 部分   | debug 用拡張枠 |

---

## 6. まとめ

### 現在有効な機能

* file / packet 監視（mock）
* hash loop による負荷再現
* バースト制御
* JSON ログ
* metrics 出力

### 将来拡張予定

* pcap 入力
* protocol / port フィルタ
* ファイルサイズ・拡張子条件
* EDR モード切替



