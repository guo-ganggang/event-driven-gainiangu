from Database import AccountParameters
from Object import AccountParameters as Account

if __name__ == '__main__':

    with open('/Users/ZHU_Chenghao/Downloads/accounts_161002.txt', 'r') as reader:
        ln_num = 1
        accounts = []
        for line in reader.readlines():
            print ln_num
            line = line.split('\t')
            if len(line) != 2:
                continue
            account = line[0]
            paras = line[1]
            domain = 0

            paras = paras.split('&')
            i = paras[1].split('=')[-1]
            s = paras[2].split('=')[-1]
            gsid = paras[7].split('=')[-1]
            accounts.append(Account(account=account, domain=domain, i=i, s=s, gsid=gsid))
            ln_num += 1
        AccountParameters.add_accounts(accounts)
