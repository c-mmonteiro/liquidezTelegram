import MetaTrader5 as mt5
import pandas as pd

class getData:
    def __init__(self) -> None:  

        self.list_ativo = []   
        self.dados = pd.DataFrame(columns=['Ativo', 
                                           'Vol Compra', 'Preco Compra', 
                                           'Vol Venda', 'Preco Venda', 
                                           'Mudanca'])
        self.dados_rolagem = pd.DataFrame(columns=['Ativo Compra', 'Ativo Venda', 
                                                   'Preco Compra', 'Preco Venda', 
                                                   'Volume', 'Lucro', 'Mudanca'])
  
        #Inicializa Metatrader 5
        if not mt5.initialize():
            print(f'Problema ao inicializar o terminal, error: {mt5.last_error()}')
            if mt5.shutdown():
                print(f'O terminal foi finalizado.')
            else:
                print(f'Problema ao finalizar o terminal, error: {mt5.last_error()}')           
    
    def addAtivo(self, ativo):
        for a in self.list_ativo:
            if a == ativo:
                print(f'Ativo {ativo} já existente!')
                return -1
        
        self.list_ativo.append(ativo)
        if not mt5.market_book_add(ativo):
            print(f'Some thing happened adding {ativo} to market book, error: {mt5.last_error()}')            
            return -1
        else:
            return 1
        
    def getAtivos(self):
        return self.list_ativo
    
    def removeAtivo(self, ativo):
        for a in self.list_ativo:
            if a == ativo:
                if not mt5.market_book_release(ativo):
                    print(f'Problema ao liberar {ativo} do book, error: {mt5.last_error()}')
                    return -1
                self.list_ativo.remove(ativo)
                
                row = self.dados[(self.dados['Ativo'] == a)]
                idx = row.index.values.tolist()
                self.dados = self.dados.drop(idx)
                return 1
        return -1
    
    def limparAtivos(self):
        print(f'-----------  Limpando Lista ----------------------\n Lista: {self.list_ativo} \n DF: {self.dados}\n---------------')
        copy_list_ativo = self.list_ativo.copy()
        for a in copy_list_ativo:
            if not mt5.market_book_release(a):
                print(f'Problema ao liberar {a} do book, error: {mt5.last_error()}')
                return -1
            self.list_ativo.remove(a)
            
            row = self.dados[(self.dados['Ativo'] == a)]
            idx = row.index.values.tolist()
            self.dados = self.dados.drop(idx)
            print(f'Ativo {a} foi removido. \n Lista: {self.list_ativo} \n DF: {self.dados}\n----------------')
        print(f'--------------------------\n Lista Final: {self.list_ativo} \n DF: {self.dados} \n ------------------')
        return 1
    
    def atualizarDados(self):
        
        if len(self.list_ativo) > 0:
            for a in self.list_ativo:
                book = mt5.market_book_get(a)
                book_frame = pd.DataFrame(book, columns=['Type', 'Price', 'Volume', 'Volume DBL'])
                buy_list = book_frame[(book_frame['Type'] == mt5.BOOK_TYPE_BUY)]
                sell_list = book_frame[(book_frame['Type'] == mt5.BOOK_TYPE_SELL)]
                print(f'-------------------------------')
                print(f'Book de {a}')
                print(f'-------------------------------')
                print(f'Compra:')
                print(buy_list)
                print(f'-------------------------------')
                print(f'Venda:')
                print(sell_list)
                print(f'-------------------------------')
                print(f'###############################')
                print(f'-------------------------------')

                if len(buy_list) != 0:
                    idx_buy = buy_list['Price'].idxmax()
                    buy = buy_list['Price'][idx_buy]
                    vol_buy = buy_list['Volume'][idx_buy]
                else:
                    buy = 0
                    vol_buy = 0
                    
                    
                if len(sell_list) != 0:
                    idx_sell = sell_list['Price'].idxmin()
                    sell = sell_list['Price'][idx_sell]
                    vol_sell = sell_list['Volume'][idx_sell]
                else:
                    sell = 0
                    vol_sell = 0
                
                if len(self.dados[(self.dados['Ativo'] == a)]) > 0:
                    row = self.dados[(self.dados['Ativo'] == a)]
                    idx = row.index.values.tolist()
                    if ((self.dados['Vol Compra'][idx[0]] == vol_buy) and
                        (self.dados['Preco Compra'][idx[0]] == buy) and
                        (self.dados['Vol Venda'][idx[0]] == vol_sell) and
                        (self.dados['Preco Venda'][idx[0]] == sell)):

                        self.dados.iloc[idx[0]] = {"Ativo": a,
                                                "Vol Compra": vol_buy, "Preco Compra": buy,
                                                "Vol Venda": vol_sell, "Preco Venda": sell,
                                                "Mudanca": 0}
                    else:
                        self.dados.iloc[idx[0]] = {"Ativo": a,
                                                "Vol Compra": vol_buy, "Preco Compra": buy,
                                                "Vol Venda": vol_sell, "Preco Venda": sell,
                                                "Mudanca": 1}

                else:
                    self.dados = self.dados.append({"Ativo": a,
                                                    "Vol Compra": vol_buy, "Preco Compra": buy,
                                                    "Vol Venda": vol_sell, "Preco Venda": sell,
                                                    "Mudanca": 1}, ignore_index=True)
                
        return self.dados
    
    def addRolagem(self, opcao_atual, opcao_futura, lucro):
        self.dados_rolagem = self.dados_rolagem.append({"Ativo Compra": opcao_atual, "Ativo Venda": opcao_futura, 
                                                        "Preco Compra": 0, "Preco Venda": 0,
                                                        "Volume": 0, "Lucro": lucro,
                                                        "Mudanca": 1}, ignore_index=True)
        

    
#h = getData()
#h.addAtivo('BBAS3')
#h.addAtivo('PETR4')
#print(f'-------- Dados Atualizados ------- \n {h.atualizarDados()}')
#print(f'-------- Dados Atualizados ------- \n {h.atualizarDados()}')
#print(f'-------- Dados Atualizados ------- \n {h.atualizarDados()}')
#print(f'-------- Dados Atualizados ------- \n {h.atualizarDados()}')