import sys
import os.path
import psycopg2
from argparse import ArgumentParser
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as tick
import seaborn as sns
sns.set_style("whitegrid")
import time

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
    
def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return (arg)

parser = ArgumentParser(description="Statement to graph")
parser.add_argument('-c', dest="connection", default="host=localhost dbname=bench user=vasilis",help="""Connection string for use by psycopg eg: "host='localhost' dbname='postgres' user='postgres'""")
parser.add_argument("-f", dest="filename", required=True, help="input file with sql statement",metavar="FILE",type=lambda x: is_valid_file(parser, x))
parser.add_argument('-i', dest="interval", required=True, help="""interval in msec""")
args = parser.parse_args()

def conn_init():
    global dbname
    dbname_found = False
    for c in args.connection.split(" "):
        if c.find("dbname=") != -1:
            dbname = c.split("=")[1]
            dbname_found = True
            break
    if not dbname_found:
        print("Missing dbname parameter in database connection string")
        sys.exit(2)
    conn = psycopg2.connect(args.connection)
    return conn

def get_data(stmt):
    conn = conn_init()
    cur = conn.cursor()
    cur.execute(stmt)
    tabledata = cur.fetchall()
    conn.close()
    return tabledata

time_lst = []
value_lst = []
    
def row_to_list():
    file = open(args.filename,'r')
    statement = file.read()
    row = get_data(statement)
    values = list(zip(*row))
    time_lst.append(values[0])
    value_lst.append(values[1])
    return time_lst, value_lst

def animate_graph(i):
    xaxis, yaxis = row_to_list()
    xaxis = xaxis[-20:]
    yaxis = yaxis[-20:]
    ax1.clear()
    ax1.plot(xaxis, yaxis)
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title(args.filename)
    plt.ylabel('value')

def main():
    ani = animation.FuncAnimation(fig, animate_graph, interval=args.interval)
    plt.show()

if __name__ == "__main__":
    main()
