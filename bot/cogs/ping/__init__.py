from .ping import Ping

def setup(bot):
    bot.add_cog(Ping(bot))