import mido
import os

key = ["Z", "X", "C", "V", "B", "N", "M",
       "A", "S", "D", "F", "G", "H", "J",
       "Q", "W", "E", "R", "T", "Y", "U"]

note = [12, 14, 16, 17, 19, 21, 23,
        24, 26, 28, 29, 31, 33, 35,
        36, 38, 40, 41, 43, 45, 47]

base_note = 3

note_map = {note[i] + base_note * 12: key[i] for i in range(len(note))}


# 定义一个函数，将音符转换为按键
def note_to_key(note):
    # 如果音符在按键对应表中，返回对应的按键，否则返回空字符串
    return note_map.get(note, '')

# 定义一个函数，将时间转换为拍数，根据MIDI文件的tick resolution来计算
def time_to_beat(time,ticks_per_beat):
    return time / ticks_per_beat

#初始化MIDI文件的tick resolution
ticks_per_beat = 0

# 定义一个函数，读取一个midi文件，返回一个列表，每个元素是一个元组，包含按键和开始时间
def read_midi(filename):
    # 打开midi文件
    midi_file = mido.MidiFile(filename)
    # 获取MIDI文件的tick resolution
    global ticks_per_beat
    ticks_per_beat = midi_file.ticks_per_beat
    # 初始化一个空列表
    result = []
    # 遍历所有轨道
    for track in midi_file.tracks:
        # 初始化当前时间为0
        current_time = 0
        # 遍历所有消息
        for msg in track:
            # 更新当前时间
            current_time += msg.time
            # 如果消息是音符开始的消息
            if msg.type == 'note_on':
                # 获取音符和力度
                note = msg.note
                velocity = msg.velocity
                # 如果力度不为0（表示音符开始）
                if velocity != 0:
                    # 将音符转换为按键
                    key = note_to_key(note)
                    # 如果按键不为空字符串（表示音符在规则之内）
                    if key != '':
                        # 将按键和开始时间作为一个元组添加到结果列表中
                        result.append((key, current_time))
    
    # 返回结果列表，按时间排序
    return sorted(result, key=lambda x: x[1])

# 定义一个函数，将结果列表转换为txt文本，并写入文件中
def write_txt(result, filename):
    if not os.path.exists('./output/'):
        os.makedirs('./output/')
    # 打开文件，以写入模式，并指定编码为utf-8
    file = open(filename + '.txt', 'w', encoding='utf-8')
    # 初始化当前拍数为0
    current_beat = 0
    # 初始化当前小节数为0
    current_bar = 0
    # 初始化当前行为空字符串
    current_line = ''
    # 初始化当前时间戳为0
    current_time = 0
    # 初始化同一时间戳下的按键列表为空
    current_keys = []

    # 遍历结果列表中的每个元组（按键和开始时间）
    for key, time in result:
        # 将开始时间转换为拍数，并向下取整（表示所在的拍）
        beat = int(time_to_beat(time,ticks_per_beat))
        # 默认以四分音符为一拍，读取当前拍数，向下取整
        bar = int(beat/4)
        if time != current_time:
            if len(current_keys) == 1:
                current_line += ''.join(current_keys)
                current_keys = []
            else:
                #删除相同键位
                for item in current_keys:
                    if current_keys.count(item) > 1:
                        if current_keys.index(item) != len(current_keys) - 1:
                            while current_keys.count(item) > 1:
                                current_keys.remove(item)
                        else:
                            while current_keys.count(item) > 1:
                                current_keys.remove(item)
                if len(current_keys) == 1:
                    current_line += ''.join(current_keys)
                    current_keys = []
                else:
                    current_line += '(' + ''.join(current_keys) + ')'
                    current_keys = []
        if time-current_time>=240: #待修改
            current_line += ' '
        if beat != current_beat:
            times = beat - current_beat
            current_line += '/' * times
        current_keys.append(key)
        # 如果当前拍数与所在的拍相同
        if bar != current_bar:
        # file.write(str(beat)+' '+str(current_beat)+' '+str(bar)+' '+str(current_bar)+' ')
            file.write(current_line+'\n')
            current_line = ''
        
        # 更新当前时间戳、拍数、小结为所在时间、拍数、小结
        current_time = time
        current_beat = beat
        current_bar = bar
    # 关闭文件
    file.close()

def input_file():
    if not os.path.exists('midi'):
        os.makedirs('midi')
        return None
    if os.listdir('midi'):
        file_list = sorted(os.listdir('./midi'))
        for i, file in enumerate(file_list):
            print(f'{i + 1}. {file}')
        selected = int(input('请选择一个文件（输入序号）：'))
        return file_list[selected-1] if selected > 0 and selected <= len(file_list) else None
    return None

# 定义一个主函数，读取一个midi文件，转换为txt文本，并写入文件中
def main(filename):
    # 读取midi文件，得到结果列表
    result = read_midi('./midi/'+filename)
    # 将结果列表转换为txt文本，并写入文件中
    write_txt(result, './output/'+filename)

# 如果这个程序是直接运行的（而不是被导入的）
if __name__ == '__main__':
    print("请将需转换的midi文件放在同目录‘midi’文件夹中")
    # 获取用户输入的文件名
    filename = input_file()
    if filename == None:
        print('midi目录下没有文件，程序自动退出')
        exit()
    # 调用主函数，传入文件名
    main(filename)