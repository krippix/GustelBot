'''
Created on 16.10.2020

@author: krippix
'''

if __name__ == '__main__':

    from GustelBOT import main
    import logging

    
    logging.basicConfig(level=logging.INFO)
    
    
    logging.debug("__main__")
    #Starting program
    main()
    logging.info("Exiting program.")
    
    