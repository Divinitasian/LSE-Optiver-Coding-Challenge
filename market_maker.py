class OptionMarketMaker:
    def __init__(self, option):
        self.primal = option
        self.dual_id = option.base_instrument_id
        