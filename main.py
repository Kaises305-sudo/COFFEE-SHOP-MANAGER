import json
import csv
from datetime import datetime



def load_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

        if not config:
            raise ValueError

        return config

    except FileNotFoundError:
        print("ERR-01: Không tìm thấy config.json")
        return None

    except (json.JSONDecodeError, ValueError, KeyError):
        print("ERR-02: config.json không hợp lệ")
        return None

 
def load_menu():
    menu = []

    try:
        with open("menu.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Kiểm tra cột
            cot_can = ["id", "name", "category", "price"]

            if reader.fieldnames is None:
                raise ValueError

            for cot in cot_can:
                if cot not in reader.fieldnames:
                    raise ValueError

            for row in reader:
                if not row["id"] or not row["name"] or not row["category"]:
                    raise ValueError

                row["price"] = int(row["price"])
                menu.append(row)

        if len(menu) == 0:
            raise ValueError

        return menu

    except FileNotFoundError:
        print("ERR-01: Không tìm thấy menu.csv")
        return None

    except (ValueError, KeyError):
        print("ERR-02: menu.csv không hợp lệ")
        return None



def load_orders():
    orders = []

    try:
        with open("orders.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                parts = line.split("|")

                
                if len(parts) != 4:
                    continue

                time = parts[0].strip()
                order_id = parts[1].strip()
                items = parts[2].strip()
                total = parts[3].strip()

                try:
                    total = int(total)
                except ValueError:
                    continue

                orders.append({
                    "time": time,
                    "order_id": order_id,
                    "items": items,
                    "total": total
                })

    except FileNotFoundError:
        
        pass

    return orders



def show_menu(menu):
    print()
    print(f"{'MÃ':<8}{'TÊN MÓN':<25}{'NHÓM':<12}{'ĐƠN GIÁ':>12}")
    print("-" * 57)

    for item in menu:
        print(
            f"{item['id']:<8}"
            f"{item['name']:<25}"
            f"{item['category']:<12}"
            f"{item['price']:>12,}"
        )

    print("-" * 57)
    print(f"Tổng số món: {len(menu)}")



def find_item(menu):
    code = input("Nhập mã món: ").strip().upper()

    for item in menu:
        if item["id"].upper() == code:
            print()
            print("Thông tin món:")
            print(f"Mã món:    {item['id']}")
            print(f"Tên món:   {item['name']}")
            print(f"Nhóm:      {item['category']}")
            print(f"Đơn giá:   {item['price']:,} VND")
            return item

    print("ERR-04: Không tìm thấy món")
    return None



def create_order(menu, config, orders):
    danh_sach_mon = []
    subtotal = 0

    print()
    print("========== TẠO ĐƠN HÀNG ==========")
    print("Nhập mã món, để trống để kết thúc.")

    while True:
        code = input("Mã món: ").strip()

       
        if code == "":
            break

        code = code.upper()

        
        item = None

        for x in menu:
            if x["id"].upper() == code:
                item = x
                break

        if item is None:
            print("ERR-04: Không tìm thấy món")
            continue

        
        try:
            qty = int(input("Số lượng: "))

            if qty <= 0:
                print("ERR-05: Số lượng phải là số nguyên dương")
                continue

        except ValueError:
            print("ERR-05: Số lượng không hợp lệ")
            continue

        
        thanh_tien = item["price"] * qty
        subtotal += thanh_tien

        danh_sach_mon.append({
            "id": item["id"],
            "name": item["name"],
            "qty": qty,
            "price": item["price"],
            "amount": thanh_tien
        })

        print(f"Đã thêm: {item['name']} x {qty}")

    
    if len(danh_sach_mon) == 0:
        print("ERR-05: Đơn hàng rỗng")
        return

    
    discount_threshold = config["discount_threshold"]
    discount_rate = config["discount_rate"]

    if subtotal >= discount_threshold:
        discount = subtotal * discount_rate
    else:
        discount = 0

    
    tien_sau_giam = subtotal - discount
    vat_rate = config["vat_rate"]

    vat = tien_sau_giam * vat_rate

    total = round(tien_sau_giam + vat)

   
    order_number = len(orders) + 1
    order_id = f"HD{order_number:03d}"

    
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    
    items_text = []

    for item in danh_sach_mon:
        text = f"{item['id']} x {item['qty']}"
        items_text.append(text)

    items_text = ", ".join(items_text)

    
    with open("orders.txt", "a", encoding="utf-8") as f:
        f.write(f"{time} | {order_id} | {items_text} | {total}\n")

    
    orders.append({
        "time": time,
        "order_id": order_id,
        "items": items_text,
        "total": total
    })

   
    print()
    print("========== HÓA ĐƠN ==========")

    for item in danh_sach_mon:
        print(
            f"{item['name']} x {item['qty']} "
            f"= {item['amount']:,} VND"
        )

    print("-" * 35)
    print(f"Tạm tính:       {subtotal:,.0f} VND")
    print(f"Giảm giá:       {discount:,.0f} VND")
    print(f"VAT:            {vat:,.0f} VND")
    print(f"TỔNG CỘNG:      {total:,} VND")
    print(f"Mã đơn:         {order_id}")
    print(f"Thời gian:      {time}")
    print("=============================")



def show_history(orders):
    if len(orders) == 0:
        print("ERR-06: Chưa có lịch sử đơn hàng")
        return

    print()
    print(f"{'THỜI GIAN':<20}{'MÃ ĐƠN':<10}{'MÓN':<25}{'TỔNG TIỀN':>15}")
    print("-" * 70)

    for order in orders:
        print(
            f"{order['time']:<20}"
            f"{order['order_id']:<10}"
            f"{order['items']:<25}"
            f"{order['total']:>15,}"
        )

    print("-" * 70)



def export_report(config, orders, menu):
    if len(orders) == 0:
        print("ERR-06: Chưa có đơn hàng để báo cáo")
        return

    total_orders = len(orders)

    revenue = 0

    for order in orders:
        revenue += order["total"]

    item_count = {}

    for order in orders:
        items = order["items"]

        parts = items.split(",")

        for part in parts:
            part = part.strip()

            if " x " not in part:
                continue

            code, qty = part.split(" x ")

            try:
                qty = int(qty)
            except ValueError:
                continue

            if code not in item_count:
                item_count[code] = 0

            item_count[code] += qty

    best_seller = None

    if item_count:
        best_code = max(item_count, key=item_count.get)

        for item in menu:
            if item["id"] == best_code:
                best_seller = {
                    "id": item["id"],
                    "name": item["name"],
                    "quantity": item_count[best_code]
                }
                break

    report = {
        "shop_name": config["shop_name"],
        "total_orders": total_orders,
        "revenue": revenue,
        "items_sold": sum(item_count.values()),
        "best_seller": best_seller
    }

    report_file = config["files"]["report"]

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(
            report,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("========== BÁO CÁO ==========")
    print(f"Tổng số đơn:       {total_orders}")
    print(f"Tổng doanh thu:    {revenue:,} VND")
    print(f"Tổng số món bán:   {sum(item_count.values())}")

    if best_seller is not None:
        print(
            f"Món bán chạy:      "
            f"{best_seller['name']} "
            f"({best_seller['quantity']} món)"
        )

    print(f"Đã lưu:            {report_file}")
    print("==============================")


def main():
    config = load_config()

    if config is None:
        return

    menu = load_menu()

    if menu is None:
        return

    orders = load_orders()

    shop_name = config["shop_name"]

    while True:
        print()
        print("=" * 40)
        print(f"========== {shop_name.upper()} ==========")
        print("1. Xem thực đơn")
        print("2. Tìm món theo mã")
        print("3. Tạo đơn hàng")
        print("4. Xem lịch sử đơn hàng")
        print("5. Xuất báo cáo doanh thu")
        print("0. Thoát")
        print("=" * 40)

        choice = input("Chọn chức năng: ").strip()

        if choice == "0":
            print("Đã thoát chương trình.")
            break

        elif choice == "1":
            show_menu(menu)

        elif choice == "2":
            find_item(menu)

        elif choice == "3":
            create_order(menu, config, orders)

        elif choice == "4":
            show_history(orders)

        elif choice == "5":
            export_report(config, orders, menu)

        else:
            print("ERR-03: Lựa chọn không hợp lệ")


if __name__ == "__main__":
    main()