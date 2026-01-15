# 採用技術バージョン調査

> 調査日: 2026年1月

---

## Python 3.14 / 3.13

| | 3.14 (2025年10月) | 3.13 (2024年10月) |
|---|---|---|
| **主要機能** | t-strings（テンプレート文字列）、Free-threaded正式サポート、Zstd圧縮、マルチインタプリタ | 新REPL（PyPy由来）、Free-threaded実験的サポート、JIT実験的サポート |
| **デバッグ** | ゼロオーバーヘッドデバッガAPI、リモートアタッチ（pdb -p PID） | カラートレースバック、改善されたエラーメッセージ |

### 3.14の注目新機能

- **PEP 750 t-strings**: f-stringsと同じ構文でカスタム文字列処理が可能
- **PEP 649 遅延アノテーション評価**: 型ヒントのパフォーマンス改善
- **PEP 779 Free-threaded Python正式対応**: GILなしでのマルチスレッド実行
- **uuid6/7/8サポート**: 新しいUUID生成関数追加
- **REPL構文ハイライト**: 入力中にカラー表示

### 注意事項

Free-threaded対応でマルチスレッドのパフォーマンスが大幅向上。ただしライブラリ互換性を確認すること。

### 参考リンク

- [Python 3.14 What's New](https://docs.python.org/3/whatsnew/3.14.html)
- [Python 3.13 What's New](https://docs.python.org/3/whatsnew/3.13.html)

---

## Rust 1.92 / 1.91

| | 1.92 (2025年12月) | 1.91 (2025年10月) |
|---|---|---|
| **主要変更** | never型のlint強化（deny-by-default）、union安全アクセス | Windows ARM64 Tier 1昇格、LLVM 21更新 |
| **コンパイラ** | unwind tableデフォルト生成、属性処理の大幅改善 | 生ポインタ警告lint追加 |

### 1.92の注目新機能

- **never型lint**: `never_type_fallback_flowing_into_unsafe`がdeny-by-default化（コンパイルエラーになる）
- **union安全アクセス**: `&raw [mut|const]`がsafeコードで使用可能
- **unwind tableデフォルト有効**: バックトレースが自動的に動作

### 1.91の注目

- **aarch64-pc-windows-msvc Tier 1**: Apple SiliconやARM WindowsでのRust開発が本格サポート

### 注意事項

1.92でnever型関連のコードがエラーになる可能性あり。事前にwarningを確認すること。

### 参考リンク

- [Rust 1.92.0](https://blog.rust-lang.org/2025/12/11/Rust-1.92.0/)
- [Rust 1.91.0](https://releases.rs/docs/1.91.0/)

---

## Next.js 16 / 15

| | 16 (2025年10月) | 15 (2024年10月) |
|---|---|---|
| **バンドラ** | Turbopackデフォルト化 | Turbopack安定版（dev） |
| **キャッシュ** | 明示的キャッシュ（use cache）、デフォルトでキャッシュなし | デフォルトでキャッシュなし（変更点） |
| **React** | React 19.2、View Transitions | React 19サポート |

### 16の注目新機能

- **"use cache"ディレクティブ**: 明示的なキャッシュ制御（ページ/コンポーネント/関数単位）
- **Turbopackデフォルト化**: 最大10x高速なFast Refresh、2-5x高速なビルド
- **proxy.ts**: middleware.tsを置き換え、ネットワーク境界を明示化
- **DevTools MCP**: AI支援デバッグ統合
- **React Compiler**: 自動メモ化でre-render削減

### 破壊的変更

- `middleware.ts` → `proxy.ts`へリネーム必須
- `params`/`searchParams`が非同期化（await必須）
- Node.js 20.9.0以上必須

### 参考リンク

- [Next.js 16](https://nextjs.org/blog/next-16)
- [Next.js 15](https://nextjs.org/blog/next-15)

---

## Redis 8 / 7

| | 8.0/8.2 (2025年5月〜) | 7.0 (2022年) |
|---|---|---|
| **データ構造** | 18種（Vector Set、JSON、Time Series等統合） | 従来のデータ構造 + モジュール |
| **パフォーマンス** | 最大91%高速化（vs 7.2）、37%メモリ削減 | 安定性重視の改善 |

### 8.0の注目新機能

- **Vector Set (Beta)**: ベクトル埋め込みの保存・検索（AI/ML用途）
- **データ構造統合**: JSON、Time Series、Bloom filterが本体に統合（別モジュール不要）
- **Redis Query Engine**: セカンダリインデックスによる高速検索
- **新Hashコマンド**: HGETEX、HSETEX、HGETDEL

### 8.2の追加

- **新BITOPオペレータ**: DIFF、ANDOR等
- **CLUSTER SLOT-STATS**: スロット単位の監視

### 注意事項

RediSearch、RedisJSON等の個別モジュールは不要になった。移行時は依存関係を確認。

### 参考リンク

- [Redis 8 GA](https://redis.io/blog/redis-8-ga/)
- [Redis 7.0](https://redis.io/blog/redis-7-generally-available/)

---

## PostgreSQL 18 / 17

| | 18 (2025年9月) | 17 (2024年9月) |
|---|---|---|
| **I/O** | 非同期I/O (AIO)サブシステム導入 | ストリーミングI/O改善 |
| **UUID** | UUIDv7ネイティブサポート | なし |
| **認証** | OAuth 2.0サポート | 従来の認証方式 |

### 18の注目新機能

- **非同期I/O (AIO)**: 最大3xのパフォーマンス向上、`io_method`設定で`io_uring`選択可能
- **uuidv7()**: タイムスタンプ順序付きUUID（主キーに最適）
- **Virtual Generated Columns**: 読み取り時に計算（デフォルト化）
- **Skip Scan**: B-treeインデックスの効率的な利用
- **Temporal Constraints**: 範囲型の時間的制約（予約システム等に有用）
- **RETURNING句拡張**: OLD/NEWで変更前後の値取得
- **Wire Protocol 3.2**: 2003年以来初のプロトコル更新

### セキュリティ変更

- MD5認証非推奨化（SCRAM推奨）
- データチェックサムがデフォルト有効

### 17の注目

- VACUUM 20x省メモリ化
- JSON_TABLE関数追加
- COPY 2x高速化

### 参考リンク

- [PostgreSQL 18 Released](https://www.postgresql.org/about/news/postgresql-18-released-3142/)
- [PostgreSQL 17 Released](https://www.postgresql.org/about/news/postgresql-17-released-2936/)

---

## まとめ

すべて2025年後半〜の最新バージョンであり、各技術で大幅なパフォーマンス改善と新機能が追加されています。

### 特に注目すべき点

| 技術 | 注目ポイント |
|------|-------------|
| **Python 3.14** | Free-threaded正式サポートでマルチスレッド性能向上 |
| **Rust 1.92** | never型lint強化、ARM Windows Tier 1 |
| **Next.js 16** | Turbopackデフォルト化とキャッシュの明示化（破壊的変更あり） |
| **Redis 8** | Vector SetでAI/MLワークロード対応、モジュール統合 |
| **PostgreSQL 18** | AIOで大幅なI/O性能向上、UUIDv7ネイティブ対応 |
