# edrsim

EDR（Endpoint Detection and Response）製品の挙動を模擬し、
**ファイル監視・パケット監視・負荷特性・ログ出力**を検証するための
**EDR シミュレーター**です。

**これはEDR製品ではありません**

本プロジェクトは以下を目的としています。

* EDR 導入時の **性能影響・負荷傾向の事前検証**
* SOC / インフラ / アプリ担当間の **共通理解用ツール**
* 「なぜ重くなるのか」を **ログとメトリクスで説明できる状態**を作る


## このリポジトリ内容が向いている人

* EDR 導入前の性能検証をしたい
* 「EDR が重い理由」を説明できる材料が欲しい
* SOC / NW / AP チーム間で共通の検証基盤が欲しい
* 擬似的にでも **本番に近い負荷**を再現したい


## 特徴

### ファイル監視（File Inspection）

* 指定ディレクトリ配下のファイル作成・更新を監視
* サイズ・拡張子・条件に応じたハッシュ計算
* 軽量スキャン / フルスキャン相当の負荷を再現
* バースト制御により「大量ファイル発生時の遅延」も再現可能


### パケット監視（Packet Inspection）

* **mock モード**：EDR 内部処理負荷の疑似生成
* **pcap モード（現在未実装で将来対応）**：実パケット再生による検証
* payload サイズに応じたハッシュ計算
* バースト検知・スロットリング挙動を再現


### メトリクス出力

* プロセス単位の CPU / メモリ使用量を定期ログ出力
* file_watcher / packet_watcher / debug それぞれ独立して取得
* multiprocessing 環境でも「どの処理の負荷か」を判別可能

### その他の特徴

edrsim は「EDR 本体」と「負荷生成用デバッガ」を完全に分離した構成を取っています。
実際の EDR 導入検証と同様に、外部からのファイル・通信イベントが、どの内部処理にどれだけの負荷を与えるかを明確に観測できる設計になっています。


## ディレクトリ構成

```
edrsim/
├─ config.yaml              # 実験条件定義（最重要）
│
├─ core/                    # 共通基盤
│   ├─ logger.py            # JSONログ / rotation / config_hash
│   ├─ metrics.py           # CPU / メモリ監視
│   ├─ burst_controller.py  # バースト制御
│   └─ config.py
│
├─ edrsim/                  # EDR 本体
│   ├─ main.py
│   ├─ file_watcher.py
│   └─ net_watcher.py
│
├─ edrsim_debug/            # 負荷生成・検証用ツール
│   ├─ main.py
│   ├─ file_generator.py
│   ├─ packet_factory.py
│   ├─ packet_mock.py
│   └─ packet_pcap.py
│
└─ README.md
```


## 実行方法

### １．設定ファイル編集

```yaml
file_inspection:
  enable: true
  paths:
    - D:/test/data

packet_inspection:
  enable: true
  mode: mock
```

### ２．EDR 本体起動

```bash
uv run -m edrsim.main
```

* ファイル監視・パケット監視が起動
* metrics / ログが同時出力される


### ３．負荷生成（別ターミナル）

```bash
uv run -m edrsim_debug.main
```

* 疑似ファイル生成
* 疑似パケット送信
* EDR の反応を再現


## config.yaml について

### ログ設定（例）

```yaml
logging:
  base_dir: logs

  default:
    level: INFO
    file: edr_mock.log
    timestamp: true
    rotation:
      type: size
      max_bytes: 10485760
      backup_count: 5
```

* サイズ / 日次ローテーション対応
* component 単位でログレベル変更可能


### バースト制御とは？

短時間にイベントが集中した場合の
**「EDR が意図的に処理を遅らせる挙動」**を再現します。

```yaml
burst_control:
  threshold: 200
  window_sec: 3
  delay_ms: 100
```

* 3 秒間に 200 件以上 → 100ms スリープ
* 実 EDR 製品の「CPU スパイク抑制」を模擬



### ログ設計

* **JSON ログ形式**
* 全ログに以下を自動付与

  * component 名
  * config_hash（設定ハッシュ）
  * timestamp（UTC）

```json
{
  "ts": "2026-01-11T13:14:30Z",
  "component": "file_watcher",
  "config_hash": "abc123...",
  "event": "inspect",
  "path": "D:/test/data/sample.exe",
  "inspect_ms": 123.4
}
```

**「このログは、どの設定で、どの処理が、どれだけ重かったのか」** を後から確認できます。

## ログ構成（Log Architecture）

edrsim では、**目的別・責務別にログファイルを分離**しています。
これにより、

* どの設定で起動したか
* どの機能が動いたか
* どの処理がどれだけ重かったか

を **後から確認や説明でき情報を記録します。

### ログファイル一覧と役割

| ログファイル                        | 内容                                |
| ----------------------------- | --------------------------------- |
| `edr-mock_main.log`           | 起動時の設定スナップショット（config 証跡）         |
| `edr-mock_file_watcher.log`   | ファイル検査の実行ログ                       |
| `edr-mock_packet_watcher.log` | パケット検査の実行ログ（通信発生時のみ）              |
| `edr-mock_metrics.main.log`   | EDR 本体プロセスの CPU / メモリ使用量          |
| `edr-mock_metrics.packet.log` | packet_watcher プロセスの CPU / メモリ使用量 |
| `edr-mock_debug.log`          | 検証用（負荷生成・mock 動作）ログ               |



### 1. 起動ログ（設定の確定）

`edr-mock_main.log`

```json
{
  "component": "edrsim",
  "event": "startup",
  "edr": { "name": "edr-mock", "mode": "behavior_based" },
  "file_inspection": {...},
  "packet_inspection": {...}
}
```

このログは **「この実行がどんな設定で行われたか」** を確定させるためのものです。
後続のすべてのログは、この設定を前提として解釈できます。



### 2. 機能別イベントログ

#### ファイル検査

`edr-mock_file_watcher.log`

```json
{
  "component": "file_inspection",
  "event": "inspect",
  "path": "D:/test/data/sample.exe",
  "hash_loops": 200,
  "inspect_ms": 18.73
}
```

* 1 ファイル単位の検査コストを可視化
* ハッシュ回数と処理時間の関係を定量評価可能

#### パケット検査

`edr-mock_packet_watcher.log`

```json
{
  "component": "packet_watcher",
  "event": "packet_inspected",
  "payload_size": 512,
  "inspect_ms": 3.2
}
```

※ 本ログは **実際に検査対象となる通信が発生した場合のみ出力**されます。
※ config.yamlのpacket_inspection>modeがmockの場合はログ出力されません。



### 3. メトリクスログ（性能影響の可視化）

#### EDR 本体プロセス

`edr-mock_metrics.main.log`

```json
{
  "event": "process_metrics",
  "cpu_percent": 98.4,
  "memory_mb": 31.02,
  "pid": 376
}
```

#### packet_watcher プロセス

`edr-mock_metrics.packet.log`

```json
{
  "event": "process_metrics",
  "cpu_percent": 1.6,
  "memory_mb": 25.7,
  "pid": 6104
}
```

* multiprocessing 環境でも **どの機能が負荷を発生させているか** を切り分け可能
* burst 制御や hash loop 設定変更の影響を定量的に評価できます



### 4. debug ログ（検証用）

`edr-mock_debug.log`

```json
{
  "component": "edrsim_debug.file_generator",
  "event": "file_created",
  "path": "D:/test/data/sample.dat"
}
```

* 本番相当ログとは分離
* 検証用の疑似挙動を明示的に区別




## 注意事項

* 本プロジェクトは **検証・学習目的**です
* 実マルウェア解析や検知ロジックは含みません
* 本番環境への直接適用は想定していません


## 今後の予定（Ideas）

* pcap モードの拡充
* Prometheus / OpenTelemetry 連携
* 負荷パターン定義（steady / burst / spike）
