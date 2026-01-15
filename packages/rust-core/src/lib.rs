//! ADMS Core - 高性能コンポーネント
//!
//! このクレートは、ADMSの高性能処理を担当します。
//! - 飛行データ解析
//! - 地理空間計算
//! - 大量データ処理

use pyo3::prelude::*;

/// Python モジュール初期化
#[pymodule]
fn adms_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", "0.1.0")?;
    Ok(())
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
