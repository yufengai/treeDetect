#plot.py
import argparse 
import sys
import matplotlib.pyplot as plt
def main(filename):
    
    f = open(filename)
    
    lines  = []
    for line in f.readlines():
        if line.find("avg") >0:
            lines.append(line)
    
    # numbers = {'1','2','3','4','5','6','7','8','9'}
    iters = []
    loss = []
    print(len(lines))
    
    fig,ax = plt.subplots()
    
    for line in lines:
        '''args = line.split(' ')
        if args[0][-1:]==':' and args[0][0] in numbers :
            iters.append(int(args[0][:-1]))            
            loss.append(float(args[2]))
           '''
        it = line.split(":")[0].strip()
        lo = line.split()[2].strip()
        # print(it,lo)
        if it.isdigit():
            # print( it , lo)
            iters.append(int(it))
            
            loss.append(float(lo))
            if int(it) % 100 ==0:
                print(it,lo)
    print(len(iters)) 
    ax.plot(iters,loss)
    plt.xlabel('iters')
    plt.ylabel('loss')
    plt.grid()
    
    #ax.set_yticks(ticks)
    plt.show()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-file",
        help = "path to log file"
        )
    args = parser.parse_args()
    main(args.file)
    #main("train.6.29.log")
