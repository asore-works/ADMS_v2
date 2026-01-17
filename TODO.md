# ADMS 開発計画

## 概要

ADMSの開発は5つのフェーズに分けて段階的に進める。各フェーズは依存関係を考慮した順序で実装する。

---

## フェーズ 0: プロジェクト基盤構築

### 0.1 モノレポ構造セットアップ

- [x] ディレクトリ構造の作成
  ```
  ADMS_v2/
  ├── apps/
  │   ├── api/          # FastAPI バックエンド
  │   └── web/          # Next.js フロントエンド
  ├── packages/
  │   ├── db/           # データベーススキーマ・マイグレーション
  │   ├── shared/       # 共有型定義・ユーティリティ
  │   └── rust-core/    # Rust高性能コンポーネント
  ├── infrastructure/
  │   ├── k8s/          # Kubernetes マニフェスト
  │   └── docker/       # Dockerfiles
  └── docs/             # ドキュメント
  ```
- [x] `.gitignore`の作成
- [x] `LICENSE`ファイルの作成（Private）

### 0.2 開発環境構築

- [x] `.mise.toml`の作成（Python 3.14, Rust 1.92, Node.js 24 LTS）
- [x] `apps/api/pyproject.toml`の作成（uv用）
- [x] `apps/web/package.json`の作成
- [x] `packages/rust-core/Cargo.toml`の作成
- [x] EditorConfig / Prettier / Ruff 設定
- [x] pre-commit hooks設定

### 0.3 CI/CD パイプライン基盤

- [x] GitHub Actions ワークフロー作成
  - [x] `ci.yml` - lint, format, type check
  - [x] `test.yml` - ユニットテスト・統合テスト
  - [ ] `build.yml` - ビルド・イメージ作成
- [x] Dependabot設定

---

## フェーズ 1: コアシステム開発

### 1.1 データベース設計

- [x] ER図の作成
- [x] PostgreSQL 18 スキーマ設計
  - [x] `users` - ユーザー・認証情報
  - [x] `organizations` - 組織情報
  - [x] `catalogs` - 機材カタログ
  - [x] `equipments` - 所有機材
  - [x] `staff` - スタッフ情報
  - [x] `flight_logs` - 飛行ログ
  - [x] `maintenance_logs` - メンテナンスログ
  - [x] `projects` - プロジェクト
  - [x] `clients` - クライアント
  - [x] `applications` - 飛行申請
- [x] UUIDv7を主キーとして採用
- [x] Temporal Constraintsの活用（予約・スケジュール）
- [x] Alembic初期マイグレーション作成

### 1.2 バックエンドAPI基盤

- [x] FastAPIプロジェクト構造
  ```
  apps/api/
  ├── src/
  │   ├── main.py
  │   ├── config/
  │   ├── db/
  │   ├── models/
  │   ├── schemas/
  │   ├── routers/
  │   ├── services/
  │   └── utils/
  └── tests/
  ```
- [x] 依存関係インストール（uv add）
  - [x] fastapi, uvicorn
  - [x] sqlalchemy, asyncpg
  - [x] alembic
  - [x] pydantic, pydantic-settings
  - [x] redis
- [x] 設定管理（pydantic-settings）
- [x] データベース接続設定（非同期）
- [x] Redis接続設定
- [x] ロギング設定
- [x] 例外ハンドリング
- [x] ヘルスチェックエンドポイント

### 1.3 認証・認可システム

- [x] JWT認証実装
- [x] リフレッシュトークン機構
- [x] RBAC（Role-Based Access Control）設計
  - [x] admin - システム管理者
  - [x] manager - 組織管理者
  - [x] operator - オペレーター
  - [x] viewer - 閲覧者
- [x] セッション管理（Redis）
- [x] パスワードハッシュ化（argon2）
- [x] 認証ミドルウェア

### 1.4 フロントエンド基盤

> **UIライブラリ: shadcn/ui を全面採用**
> - 全UIコンポーネントはshadcn/uiを使用
> - テーマ・スタイリングはshadcn/uiの設計に準拠
> - MCP shadcnサーバーを活用してコンポーネント検索・実装例参照

- [x] Next.js 16プロジェクト作成
  ```
  apps/web/
  ├── src/
  │   ├── app/
  │   ├── components/
  │   │   └── ui/          # shadcn/ui コンポーネント
  │   ├── hooks/
  │   ├── lib/
  │   ├── stores/
  │   └── types/
  └── tests/
  ```
- [x] shadcn/ui 初期化（`npx shadcn@latest init`）
- [x] 依存関係インストール
  - [x] shadcn/ui 基本コンポーネント（button, card, form, input, table等）
  - [x] TanStack Query
  - [x] Zustand（状態管理）
  - [x] zod（バリデーション）
  - [x] date-fns
- [x] Tailwind CSS設定（shadcn/uiテーマ統合）
- [x] 認証フロー（ログイン/ログアウト）- shadcn/ui form使用
- [x] レイアウトコンポーネント - shadcn/ui準拠
- [x] ダッシュボードページ骨格

### 1.5 モデル項目修正・最適化

各モデルのレビューと必要な修正を実施。

#### 1.5.1 Organization モデル
- [ ] インデックス最適化（name, code, is_active）
- [ ] unique制約確認（code）
- [ ] バリデーション追加（email, phone形式）
- [ ] 組織ロゴURL追加検討

#### 1.5.2 User モデル
- [x] 基本設計完了
- [ ] パスワード履歴テーブル追加検討
- [ ] ログインログ記録検討
- [ ] 最終ログイン日時追加

#### 1.5.3 Catalog モデル
- [ ] specifications を JSON型（JSONB）に変更
- [ ] 複合インデックス追加（organization_id, category, is_active）
- [ ] カタログコード（SKU）フィールド追加
- [ ] バージョン管理フィールド追加検討

#### 1.5.4 Equipment モデル
- [ ] unique制約追加（organization_id, serial_number）
- [ ] 複合インデックス追加（organization_id, status, catalog_id）
- [ ] QRコード自動生成処理追加
- [ ] 稼働率計算プロパティ追加
- [ ] 総飛行時間からアラート生成機能

#### 1.5.5 Staff モデル
- [ ] full_name プロパティ追加（user.first_name + user.last_name）
- [ ] 有効な資格数カウントプロパティ
- [ ] スタッフ稼働状況ステータス検討
- [ ] 複合インデックス追加（organization_id, is_available）

#### 1.5.6 License モデル
- [ ] 期限切れアラート閾値設定（30日前、7日前など）
- [ ] 複合インデックス追加（staff_id, expiry_date）
- [ ] 自動更新通知フラグ追加
- [ ] 資格レベル（初級/中級/上級）フィールド検討

#### 1.5.7 Client モデル
- [ ] インデックス追加（company_name, is_active）
- [ ] 取引開始日フィールド追加
- [ ] 総取引額プロパティ追加
- [ ] 優先度フィールド（VIP等）追加検討

#### 1.5.8 Project モデル
- [ ] プロジェクトコードunique制約追加（code）
- [ ] 進捗率計算プロパティ追加
- [ ] 予算達成率プロパティ追加
- [ ] 複合インデックス追加（organization_id, status, start_date）
- [ ] プロジェクトマネージャー（staff_id）フィールド追加検討

#### 1.5.9 ProjectAssignment モデル
- [ ] unique制約追加（project_id, staff_id, role）
- [ ] アサイン時間（工数）フィールド追加検討
- [ ] 稼働率（allocation_percentage）追加検討

#### 1.5.10 FlightLog モデル
- [ ] 複合インデックス追加（equipment_id, takeoff_time）
- [ ] 複合インデックス追加（pilot_id, takeoff_time）
- [ ] 飛行距離自動計算（GeoJSONから）
- [ ] 天候データAPI連携準備
- [ ] 飛行ログのステータス（DRAFT/COMPLETED）追加検討

#### 1.5.11 MaintenanceLog モデル
- [ ] total_cost 自動計算（labor_cost + parts_cost）
- [ ] 複合インデックス追加（equipment_id, scheduled_date）
- [ ] parts_replaced を JSON型（JSONB）に変更
- [ ] checklist_items を JSON型（JSONB）に変更
- [ ] 承認ワークフロー追加検討

#### 1.5.12 FlightApplication モデル
- [ ] DIPS API連携フィールド追加
- [ ] 申請ステータス自動更新機能
- [ ] 複合インデックス追加（organization_id, status, valid_until）
- [ ] 申請テンプレート機能検討
- [ ] 承認フロー（申請者、承認者）追加検討

---

## フェーズ 2: 業務機能開発

> **フロントエンド実装方針**
> - 全UIはshadcn/uiコンポーネントを使用
> - 実装前にMCP shadcnで該当コンポーネントの実装例を参照
> - フォーム: shadcn/ui form + react-hook-form + zod
> - テーブル: shadcn/ui table + @tanstack/react-table
> - ダイアログ・モーダル: shadcn/ui dialog/sheet

### 2.1 カタログ管理

- [ ] **バックエンド**
  - [ ] カタログCRUD API
  - [ ] カテゴリ管理
  - [ ] 画像アップロード（S3互換ストレージ）
  - [ ] 仕様書PDF管理
- [ ] **フロントエンド**
  - [ ] カタログ一覧ページ
  - [ ] カタログ詳細ページ
  - [ ] カタログ登録/編集フォーム
  - [ ] カテゴリフィルター
  - [ ] 検索機能

### 2.2 機材管理

- [ ] **バックエンド**
  - [ ] 機材CRUD API
  - [ ] シリアル番号管理
  - [ ] 稼働状態管理（稼働中/保管中/メンテナンス中/退役）
  - [ ] カタログとのリレーション
- [ ] **フロントエンド**
  - [ ] 機材一覧ページ
  - [ ] 機材詳細ページ（履歴タイムライン）
  - [ ] 機材登録/編集フォーム
  - [ ] QRコード生成
  - [ ] 状態フィルター

### 2.3 スタッフ管理

- [ ] **バックエンド**
  - [ ] スタッフCRUD API
  - [ ] 資格・ライセンス管理
  - [ ] 有効期限アラート
  - [ ] 稼働スケジュール
- [ ] **フロントエンド**
  - [ ] スタッフ一覧ページ
  - [ ] スタッフ詳細ページ
  - [ ] 資格登録フォーム
  - [ ] スケジュールカレンダー
  - [ ] 期限切れアラート表示

### 2.4 飛行ログ

- [ ] **バックエンド**
  - [ ] 飛行ログCRUD API
  - [ ] 位置情報（GeoJSON）
  - [ ] 飛行時間自動計算
  - [ ] 機材・パイロット紐付け
  - [ ] 統計集計API
- [ ] **フロントエンド**
  - [ ] 飛行ログ一覧ページ
  - [ ] 飛行ログ詳細ページ（地図表示）
  - [ ] 飛行ログ登録フォーム
  - [ ] フライトマップ（Leaflet/Mapbox）
  - [ ] 統計ダッシュボード

### 2.5 メンテナンスログ

- [ ] **バックエンド**
  - [ ] メンテナンスログCRUD API
  - [ ] 定期点検スケジュール
  - [ ] 部品交換履歴
  - [ ] 次回点検アラート
- [ ] **フロントエンド**
  - [ ] メンテナンスログ一覧ページ
  - [ ] メンテナンス詳細ページ
  - [ ] 点検チェックリストフォーム
  - [ ] メンテナンスカレンダー

### 2.6 プロジェクト管理

- [ ] **バックエンド**
  - [ ] プロジェクトCRUD API
  - [ ] ステータス管理（計画中/進行中/完了/キャンセル）
  - [ ] 機材・スタッフアサイン
  - [ ] スケジュール管理
- [ ] **フロントエンド**
  - [ ] プロジェクト一覧ページ
  - [ ] プロジェクト詳細ページ
  - [ ] ガントチャート
  - [ ] リソースアサイン画面

### 2.7 クライアント管理

- [ ] **バックエンド**
  - [ ] クライアントCRUD API
  - [ ] 連絡先管理
  - [ ] プロジェクト履歴
  - [ ] 請求情報管理
- [ ] **フロントエンド**
  - [ ] クライアント一覧ページ
  - [ ] クライアント詳細ページ
  - [ ] 取引履歴表示
  - [ ] 連絡先フォーム

---

## フェーズ 3: 外部連携・高度機能

### 3.1 DIPS2.0 API連携

- [ ] DIPS2.0 API調査・仕様確認
- [ ] **バックエンド**
  - [ ] DIPS2.0 APIクライアント実装
  - [ ] 飛行計画申請API
  - [ ] 申請状況取得API
  - [ ] 申請履歴管理
- [ ] **フロントエンド**
  - [ ] 申請フォーム（DIPS連携）
  - [ ] 申請状況ダッシュボード
  - [ ] 申請履歴一覧

### 3.2 Rust高性能コンポーネント

- [ ] PyO3によるPythonバインディング
- [ ] 飛行データ解析モジュール
- [ ] 大量ログデータ処理
- [ ] 地理空間計算（空域判定等）

### 3.3 通知システム

- [ ] メール通知（期限切れアラート等）
- [ ] Webhook連携
- [ ] プッシュ通知（将来的なモバイル対応準備）

### 3.4 レポート・エクスポート

- [ ] PDF帳票生成
- [ ] Excel/CSVエクスポート
- [ ] 飛行実績レポート
- [ ] メンテナンス報告書

---

## フェーズ 4: インフラ・本番環境

### 4.1 コンテナ化

- [ ] `apps/api/Dockerfile`作成
- [ ] `apps/web/Dockerfile`作成
- [ ] `docker-compose.yml`（開発環境）
- [ ] マルチステージビルド最適化

### 4.2 Kubernetes（k3s）

- [ ] Namespace設計
- [ ] Deployment マニフェスト
- [ ] Service / Ingress設定
- [ ] ConfigMap / Secret管理
- [ ] PersistentVolumeClaim（PostgreSQL, Redis）
- [ ] HPA（Horizontal Pod Autoscaler）

### 4.3 CI/CD完成

- [ ] ステージング環境デプロイ
- [ ] 本番環境デプロイ
- [ ] ブルーグリーンデプロイメント
- [ ] ロールバック手順

### 4.4 監視・運用

- [ ] ログ収集（Loki / Fluentd）
- [ ] メトリクス収集（Prometheus）
- [ ] ダッシュボード（Grafana）
- [ ] アラート設定
- [ ] バックアップ戦略

---

## フェーズ 5: 品質保証・ドキュメント

### 5.1 テスト

- [ ] ユニットテスト（pytest, vitest）
- [ ] 統合テスト
- [ ] E2Eテスト（Playwright）
- [ ] 負荷テスト
- [ ] カバレッジ目標: 80%以上

### 5.2 ドキュメント

- [ ] API仕様書（OpenAPI / Swagger）
- [ ] 開発者ガイド
- [ ] 運用マニュアル
- [ ] ユーザーマニュアル

### 5.3 セキュリティ

- [ ] OWASP Top 10対策確認
- [ ] 依存関係脆弱性スキャン
- [ ] ペネトレーションテスト
- [ ] セキュリティレビュー

---

## マイルストーン

| フェーズ | 完了条件 |
|---------|----------|
| Phase 0 | 開発環境が動作し、CI/CDが稼働 |
| Phase 1 | 認証付きAPIとフロントエンド骨格が完成 |
| Phase 2 | 全業務機能のCRUDが動作 |
| Phase 3 | DIPS2.0連携と高度機能が動作 |
| Phase 4 | 本番環境へデプロイ完了 |
| Phase 5 | テスト・ドキュメント完備 |

---

## 優先度と依存関係

```
Phase 0 ──→ Phase 1 ──→ Phase 2 ──→ Phase 3
                │                      │
                └──────→ Phase 4 ←─────┘
                              │
                              ↓
                         Phase 5
```

- Phase 0は全ての基盤となるため最優先
- Phase 1の認証基盤がないとPhase 2以降は進められない
- Phase 4はPhase 1完了後から並行して進行可能
- Phase 3はPhase 2の各機能と並行して進行可能
