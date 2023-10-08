import pandas as pd


def show_orders(symbol, gNetCode, gNetRoot, client):
    if gNetCode is None:
        print('show_orders: gNetCode=', gNetCode)
        return False

    try:
        orders = client.get_orders(symbol, recvWindow=59000)
        df = pd.DataFrame(orders,
                          columns=['clientOrderId', 'price', 'origQty', 'executedQty', 'cummulativeQuoteQty', 'status',
                                   'type', 'side'])
        sorted_df = df.sort_values(by='clientOrderId')

        file_path = f"{gNetRoot}orders\\{gNetCode}.txt"
        with open(file_path, "w") as file:
            filtered_df = sorted_df[sorted_df['clientOrderId'].str.contains(gNetCode)]
            file.write(filtered_df.to_string(index=False))

        return True
    except Exception as e:
        print("Ошибка:", str(e))
        return False
