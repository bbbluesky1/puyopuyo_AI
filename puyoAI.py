import pprint
import random
import _pickle as cPickle
import time
from PIL import Image

#x列の高さを数える
def search_height(field,x):
    return len([y[x] for y in field if y[x] != 0])

def next_create():
    color_type = ["G","Y","B","R"]
    return [random.choice(color_type) for i in range(2)]

def possible_moves(field,next):
    all_possible_moves = []
    #ぷよを横にしておいた時の全ての置き方
    for x in range(6):
        if x+1 < 6:
            #14段目まで埋まってないとき
            if search_height(field,x) < 14 and search_height(field,x+1) < 14:
                copy_field = cPickle.loads(cPickle.dumps(field, -1))
                #ぷよぷよの仕様で14段目のぷよは消える
                if search_height(field,x)+1 != 14:
                    copy_field[-(search_height(field,x)+1)][x] = next[0]
                #ぷよぷよの仕様で14段目のぷよは消える
                if search_height(field,x+1)+1 != 14:
                    copy_field[-(search_height(field,x+1)+1)][x+1] = next[1]
                all_possible_moves.append(copy_field)
    #2つとも同じ色のぷよの時は置いた後のフィールドが被る置き方があるからそこをカット
    if next[0] != next[1]:
        for x in range(6):
            if x+1 < 6:
                #14段目まで埋まってないとき
                if search_height(field,x) < 14 and search_height(field,x+1) < 14:
                    copy_field = cPickle.loads(cPickle.dumps(field, -1))
                    #ぷよぷよの仕様で14段目のぷよは消える
                    if search_height(field,x)+1 != 14:
                        copy_field[-(search_height(field,x)+1)][x] = next[1]
                    #ぷよぷよの仕様で14段目のぷよは消える
                    if search_height(field,x+1)+1 != 14:
                        copy_field[-(search_height(field,x+1)+1)][x+1] = next[0]
                    all_possible_moves.append(copy_field)
    #ぷよを縦にしておいた時の全ての置き方
    for x in range(6):
        if search_height(field,x) <= 12:
            copy_field = cPickle.loads(cPickle.dumps(field, -1))
            copy_field[-(search_height(field,x)+1)][x] = next[0]
            #ぷよぷよの仕様で14段目のぷよは消える
            if search_height(field,x)+2 != 14:
                copy_field[-(search_height(field,x)+2)][x] = next[1]
            all_possible_moves.append(copy_field)
    #2つとも同じ色のぷよの時は置いた後のフィールドが被る置き方があるからそこをカット
    if next[0] != next[1]:
        for x in range(6):
            if search_height(field,x) <= 12:
                copy_field = cPickle.loads(cPickle.dumps(field, -1))
                copy_field[-(search_height(field,x)+1)][x] = next[1]
                #ぷよぷよの仕様で14段目のぷよは消える
                if search_height(field,x)+2 != 14:
                    copy_field[-(search_height(field,x)+2)][x] = next[0]
                all_possible_moves.append(copy_field)
    return all_possible_moves

def count(field,y,x):
    global n
    c = field[y][x]
    field[y][x] = 1
    n +=1

    if x+1 < 6 and field[y][x+1] == c and c != 1:
        count(field,y,x+1)
    if y+1 < 14 and field[y+1][x] == c and c != 1:
        count(field,y+1,x)
    if x-1 >= 0 and field[y][x-1] == c and c != 1:
        count(field,y,x-1)
    if y-1 >= 0 and field[y-1][x] == c and c != 1:
        count(field,y-1,x)
    return n

def drop(field,y,x):
    while y >= 0:
        if y > 0:
            field[y][x] = field[y-1][x]
            y -= 1
        #14段目は空白
        else:
            field[y][x] = 0
            y -= 1
    return field

def chain(field,chain_count):
    global n
    copy_field = cPickle.loads(cPickle.dumps(field, -1))
    #4つ以上繋がっているところにフラグを立てる
    for y in range(14):
        for x in range(6):
            n = 0
            if field[y][x] != 0 and count(cPickle.loads(cPickle.dumps(field, -1)),y,x) >= 4:
                copy_field[y][x] = 1
    #フラグが一つもなかったら終了
    flag_count = 0
    for y in copy_field:
        flag_count += y.count(1)
    if flag_count == 0:
        return copy_field,chain_count
    #浮いてるぷよを落とす
    for y in range(14):
        for x in range(6):
            if copy_field[y][x] == 1:
                drop(copy_field,y,x)
    chain_count +=1
    return chain(copy_field,chain_count)

def height_evaluation(field):
    point = 0
    for x in range(6):
        if x == 0 or x == 5:
            point += len([y[x] for y in field if y[x] != 0])*2
        if x == 1 or x == 4:
            point += len([y[x] for y in field if y[x] != 0])
    return point

#各列にそれぞれの色のぷよを2つ落とした時の最大連鎖数
def feature_chain_evaluation(field):
    chain_counts = []
    color_type = ["G","Y","B","R"]
    for x in range(6):
        for color in color_type:
            copy_field = cPickle.loads(cPickle.dumps(field, -1))
            if [y[x] for y in field].count(0) > 2:
                copy_field[-(search_height(copy_field,x)+1)][x] = color
                copy_field[-(search_height(copy_field,x)+2)][x] = color
                chain_counts.append(chain(copy_field,0)[1])
            else:
                chain_counts.append(0)
    return max(chain_counts)

def count_evaluation(field):
    global n
    point = 0
    for y in range(14):
        for x in range(6):
            if field[y][x] != 0:
                n = 0
                point += count(cPickle.loads(cPickle.dumps(field, -1)),y,x)**2
    return point

def beam_search(depth0s,next,depth):
    print("現在の探索深さ:{}".format(depth))
    if depth > 10:
        return depth0s
    evaluation_results = []
    for depth0 in depth0s:
        for depth1 in possible_moves(depth0[1],next):
            #ぷよが消える置き方をしない,3列目の12段目に置かない
            if chain(depth1,0)[1] == 0 and depth1[2][2] == 0:
                evaluation_results.append([depth0[0],depth1,feature_chain_evaluation(depth1)*10 + height_evaluation(depth1) + count_evaluation(depth1)])
    return beam_search(sorted(evaluation_results, key=lambda x:x[2], reverse=True)[:50],next_create(),depth+1)

def next_move(field,next):
    evaluation_results = []
    for depth1 in possible_moves(field,next[0]):
        #ぷよが消える置き方をしない,3列目の12段目に置かない
        if chain(depth1,0)[1] == 0 and depth1[2][2] == 0:
            for depth2 in possible_moves(depth1,next[1]):
                #ぷよが消える置き方をしない,3列目の12段目に置かない
                if chain(depth2,0)[1] == 0 and depth2[2][2] == 0:
                    evaluation_results.append([depth1,depth2,feature_chain_evaluation(depth2)*10 + height_evaluation(depth2) + count_evaluation(depth2)])
    #評価値の合計が一番高い手を採用
    #dic = {フィールド:評価値}
    dic = {}
    beam_search_result = beam_search(sorted(evaluation_results, key=lambda x:x[2], reverse=True)[:50],next[2],3)
    for i in beam_search_result:
        #フィールドを文字列にして辞書のkeyにする
        #初期値を入れる(0)
        dic["".join([str(x) for y in i[0] for x in y])] = 0
    for i in beam_search_result:
        #フィールドに評価値を加算
        dic["".join([str(x) for y in i[0] for x in y])] += i[2]
    #評価値の合計が最も高いフィールド(文字列)
    final_choice = sorted(dic.items(), key=lambda x:x[1], reverse=True)[0][0]
    #文字列から二次元配列に直してreturn
    return [[n if n != "0" else 0 for n in final_choice[i:i+6]] for i in range(0,len(final_choice),6)]

def field_to_img(field):
    green = Image.open("img/green.png")
    yellow = Image.open("img/yellow.png")
    blue = Image.open("img/blue.png")
    red = Image.open("img/red.png")
    blank = Image.open("img/blank.png")
    imgs = [green,yellow,blue,red,blank]
    color_type = ["G","Y","B","R",0]
    field_img = Image.new("RGB", (green.width*6, green.height*14))
    start_y = 0
    for y in field:
        field_x_img = Image.new("RGB", (green.width*6, green.height))
        start_x = 0
        for x in y:
            for img,color in zip(imgs,color_type):
                if x == color:
                    field_x_img.paste(img, (start_x, 0))
                    start_x += img.width
        field_img.paste(field_x_img, (0, start_y))
        start_y += field_x_img.height
    return field_img

def main():
    start = time.time()
    imgs = []
    field = initial_field
    next = [next_create(),next_create(),next_create()]
    for i in range(30):
        field = next_move(field,next)
        pprint.pprint(field)
        imgs.append(field_to_img(field))
        next.pop(0)
        next.append(next_create())
    imgs[0].save("result.gif",save_all=True, append_images=imgs[1:], optimize=False, duration=500, loop=0)
    imgs[-1].save("result.png")
    print("処理時間:{}秒".format(time.time()-start))

if __name__ == "__main__":
    initial_field = [[0]*6 for i in range(14)]
    main()
