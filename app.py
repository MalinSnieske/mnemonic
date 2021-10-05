from dataclasses import dataclass

from flask import Flask, request

app = Flask(__name__)


@dataclass
class Account:
    id: int
    name: str
    available_cash: int

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "availableCash": self.available_cash
        }


@dataclass
class Transaction:
    id: int
    success: bool
    cash_amount: float
    source_account: int
    destination_account: int

    def serialize(self):
        return {
            "id": self.id,
            "success": self.success,
            "cashAmount": self.cash_amount,
            "sourceAccount": self.source_account,
            "destinationAccount": self.destination_account
        }


DATABASE = dict()
DATABASE["accounts"] = dict()
DATABASE["transactions"] = dict()

DATABASE["accounts"][0] = Account(0, "Konto1", 1000)
DATABASE["accounts"][1] = Account(1, "Konto2", 0)
DATABASE["accounts"][2] = Account(2, "Konto3", 1_000_000)


def new_account_id():
    return len(DATABASE["accounts"].values())


def new_transaction_id():
    return len(DATABASE["transactions"].values())


@app.route("/accounts")
def get_accounts():
    accounts = DATABASE["accounts"]
    output = []
    for account in accounts.values():
        account_data = {'name': account.name, 'availableCash': account.available_cash}
        output.append(account_data)
    return {"accounts": output}


@app.route('/accounts/<id>')
def get_account(id):
    account: Account = DATABASE["accounts"][int(id)]
    return {'name': account.name, 'availableCash': account.available_cash}


@app.route('/accounts', methods=['POST'])
def add_account():
    data = request.get_json()
    account = Account(new_account_id(), data["name"], data["availableCash"])
    DATABASE["accounts"][account.id] = account
    return {'id': account.id}


@app.route('/accounts/<id>', methods=['DELETE'])
def delete_account(id):
    account = DATABASE["accounts"].get(int(id))
    if account is None:
        return {"message": "Account not found"}, 404
    del DATABASE["accounts"][account.id]
    return {"message": "Account deleted"}

@app.route("/transactions")
def get_transactions():
    transactions = DATABASE["transactions"]
    output = []
    for transaction in transactions.values():
        transaction_data = {'success': transaction.success, 'cashAmount': transaction.cash_amount,
                            'sourceAccount': transaction.source_account, 'destinationAccount': transaction.destination_account}
        output.append(transaction_data)
    return {"transactions": output}


@app.route('/transaction/<id>', methods=["POST"])
def make_transaction(id):
    data = request.get_json()
    print(data)
    source: Account = DATABASE["accounts"].get(int(id))
    destination: Account = DATABASE["accounts"].get(int(data["to"]))
    if source is None or destination is None:
        return {"message": "Account not found"}, 404
    elif source.available_cash < data["amount"]:
        return {"message": "Insufficient amount"}, 400
    else:
        source.available_cash -= data["amount"]
        destination.available_cash += data["amount"]
        transaction = Transaction(new_transaction_id(), True, data["amount"], source.id, destination.id)
        DATABASE["transactions"][transaction.id] = transaction
        return transaction.serialize()


if __name__ == '__main__':
    app.run()
