"""
数据库清理工具
用于后台测试用例执行后还原数据状态
"""
import pymysql
from config import get_config
from utils.logger import setup_logger


class DBHelper:
    def __init__(self):
        cfg = get_config()
        db_cfg = cfg.get("db", {})
        self.logger = setup_logger()
        self.conn = pymysql.connect(
            host=db_cfg.get("host"),
            port=db_cfg.get("port"),
            user=db_cfg.get("user"),
            password=db_cfg.get("password"),
            database=db_cfg.get("database"),
            charset="utf8mb4",
            autocommit=True
        )
        self.cursor = self.conn.cursor()

    def execute(self, sql, params=None):
        """执行单条SQL"""
        # self.logger.info(f"[DB] 执行: {sql} params={params}")
        self.cursor.execute(sql, params or ())

    def execute_many(self, sql_list):
        """批量执行多条SQL"""
        for sql in sql_list:
            self.execute(sql)

    def close(self):
        self.cursor.close()
        self.conn.close()


def clean_three_way_match_data(invoice_nos=None):
    """
    清理三单匹配相关数据
    通过多表关联DELETE一次性清理所有关联数据

    Args:
        invoice_nos: 发票编号（t_srm_supplier_invoice.invoice_no）
    """
    logger = setup_logger()

    if not invoice_nos:
        logger.info("[清理] 未传入invoice_no，跳过清理")
        return

    try:
        db = DBHelper()
    except Exception as e:
        logger.error(f"[清理] 数据库连接失败: {e}")
        return

    try:
        placeholders = ",".join(["%s"] * len(invoice_nos))
        sql = f"""
            DELETE d,c,b,a,e,f,g
            FROM t_srm_supplier_invoice d
            LEFT JOIN t_srm_supplier_invoice_item c ON d.id=c.invoice_id
            LEFT JOIN t_srm_three_way_match b ON d.id=b.invoice_id
            LEFT JOIN t_srm_three_way_match_item a ON b.id=a.match_id
            LEFT JOIN t_srm_match_make_up_order e on b.id=e.match_id
            LEFT JOIN t_srm_expense_order_deduction f on b.id=f.match_id
            LEFT JOIN t_srm_pre_settlement_deduction g on b.id=g.match_id
            WHERE d.invoice_no IN ({placeholders})
        """
        db.execute(sql, invoice_nos)
    except Exception as e:
        logger.warning(f"[清理] SQL清理失败: {e}，请手动检查数据库")
    finally:
        db.close()


if __name__ == "__main__":
    clean_three_way_match_data(invoice_nos=["26442000007652675806"])
