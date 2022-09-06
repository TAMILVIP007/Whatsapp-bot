import json
import random

import time
import copy
from time import time

import requests
from PyDictionary import PyDictionary
import pydoodle
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys

# list of emojis for the fig game
emojis = ["🍓", "🥭", "🥥", "🍎", "🍇", "🫐", "🍒", "🌶️", "🥒", "🍅", "🥦", "🍞", "🥯", "🍕", "🍔", "🍫", "🍿", "🍩",
          "🥤", "🥜", "🍼", "🍨", "🍬", "🍭"]

# list of emojis number for minesweeper
emoj = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]


# class for sticker maker
class karma_sticker:
    # function for creating sticker from image
    def k_send_sticker(self, driver, message):

        if message.type == 'video' and hasattr(message,
                                               'caption') and message.caption == '#sticker':  # video and gif can't converted
            driver.chat_send_message(message.chat_id, "Sry can't make sticker")
        elif hasattr(message, 'caption') and message.caption == '#sticker':

            a = (driver.download_media(message, True))
            print(a)
            try:
                if message.chat_id in [
                    '919675642959-1606755119@g.us',
                    '919557666582-1580308963@g.us',
                ]:  # custom setting you can ignore it
                    driver.driver.switch_to.window(driver.driver.window_handles[0])
                    driver.send_image_as_sticker(a, '919675642959-1606756367@g.us')
                else:
                    print("Sending sticker")

                    driver.driver.switch_to.window(driver.driver.window_handles[0])
                    driver.send_image_as_sticker(a, message.chat_id)  # sending converted sticker
                    print("Sticker sent")
            except Exception as ex:
                print(ex)
                driver.chat_send_message(message.chat_id, "Sry can't make sticker")


# class for word game
class karma_word_game:
    # initilizing some helping variables
    def __init__(self, s_board, players):
        self.start = 0
        self.mean_dict=PyDictionary()
        self.c = 0  # check whether 3 people voted or not for skipping a word
        self.already_solved = 0
        self.score_board = s_board
        self.players = players
        self.skip_list_players = []
        with open('level2.json', 'r+') as f:
            self.li = json.load(f)  # json file containing all words

    def new_word(self, driver, message):
        self.word = random.choice(self.li['data'])

        l_word = len(self.word)
        gap = int(3.8 / 10 * l_word)  # finding how many letters will be hidden in the word
        gap_list = random.sample(range(l_word - 1), gap)
        w = list(self.word)
        for i in gap_list:
            w[i] = '_ '
        self.w_todisplay = "".join(w)  # getting the final word to display

        driver.wapi_functions.sendMessage(message.chat_id,
                                          "Guess the word:\n" + "*" + self.w_todisplay.upper() + "*")
        print(self.word)
        self.already_solved = 0
        self.c = 0
        self.skip_list_players = []

    # function to start the game
    def wgame_start(self, driver, message):

        driver.chat_send_message(message.chat_id,
            "*Word Game Started!* \n\nSend #help_wgame to see all commands.")
        self.new_word(driver, message)
        self.start = 1

    # function to check answer given by user is right or not
    def ans(self, driver, message, ans):

        if ans.lower() == self.word:  # checking whether answer  given is right or not
            if self.already_solved == 0:
                self.already_solved = 1
                d = self.mean_dict.meaning(self.word)
                out = ""
                if d != None:
                    for key, value in d.items():
                        out += f"~{key} :{value[0]}" + "\n"
                driver.chat_send_message(
                    message.chat_id, f"Right Answer 💯!\n\nWord Definition:\n{out}"
                )


                self.score_board[self.players[message.sender.id]] += 1  # updating user score if he/she is right
                return 1

            else:
                driver.chat_send_message(message.chat_id,
                    "Already Answered 😓!\n\nSend #score to check the scores.\nSend #currword to see current word")

        else:
            driver.chat_send_message(message.chat_id,"Wrong! Think more 🧠\n\nType #currword to see current guessing word.")
        return 0

    # function to enter in the game
    def enter_game(self,driver, message, name):

        self.players[message.sender.id] = name  # new player added
        self.score_board[self.players[message.sender.id]] = 0

        driver.chat_send_message(message.chat_id,
            "You have entered the game 👍🏽\n\nAnswer by sending #ans your answer here")

    # function to skip or go to next word
    def skip(self, driver, message):
        if self.already_solved != 0 or self.c >= 3:
            return
        if message.sender.id in self.skip_list_players:  # checking whether the player is already voted or not
            driver.chat_send_message(message.chat_id,"You already voted to skip\n" + str(
                3 - self.c) + " vote needed now to skip this word")
        else:
            self.c += 1
            if self.c == 3:
                d = self.mean_dict.meaning(self.word)
                out = ""
                if d != None:
                    for key, value in d.items():
                        out += f"~{key} :{value[0]}" + "\n"
                driver.chat_send_message(message.chat_id,"The Right Answer is:\n" + "*" + self.word + "*\n\nWord Definition:\n"+out)
                self.already_solved = 1
                self.new_word(driver, message)
            else:
                driver.chat_send_message(
                    message.chat_id,
                    f"{str(3 - self.c)} vote needed now to skip the word",
                )

                self.skip_list_players.append(message.sender.id)

    # function to show current word
    def current_word(self, driver, message):
        driver.chat_send_message(message.chat_id, "Guess the word:\n" + "*" + self.w_todisplay.upper() + "*")

    # function to show the scoreboard
    def show_score(self, driver,message):
        if len(self.score_board) != 0:
            print(self.score_board)
            out = "".join(
                f"{str(value)}--> {str(key)}" + "\n"
                for key, value in dict(
                    sorted(
                        self.score_board.items(),
                        key=lambda item: item[1],
                        reverse=True,
                    )
                ).items()
            )

            driver.chat_send_message(message.chat_id,"-----------Score Board-----------\n\n" + out)
        else:
            driver.chat_send_message(message.chat_id,"Empty Score Board")


# class for tic tac toe game
class tic_tac_game:

    def __init__(self, driver, message, p1, p2):
        # player list
        self.players = [p1, p2]

        # choosing which player chance randomly
        self.chance = random.choice(range(2))

        # status of game who won or loss
        self.status = ""

        # initial game map
        self.g_map = [["⬜" for _ in range(3)] for _ in range(3)]

        # list of place to be marked
        self.to_be_marked_list = [str(i) for i in range(1, 10)]

        # sending empty game board
        out = self.list_to_string(self.g_map)
        out2 = f"Game started {str(driver.get_contact_from_id(self.players[0]).push_name)} vs {str(driver.get_contact_from_id(self.players[1]).push_name)} ⚔️"

        out3 = f"First {str(driver.get_contact_from_id(self.players[self.chance]).push_name)} your turn \nSend #(box number) to place your mark on board."

        driver.chat_send_message(message.chat_id, out + "\n" + out2)
        driver.chat_send_message(message.chat_id, out3)

    def list_to_string(self, li):
        s = [''.join(li[i]) for i in range(len(li))]
        s = "\n".join(s)
        return s

    def mark(self, driver, message, m):
        if self.players[self.chance] == str(message.sender.id):

            if m in self.to_be_marked_list:

                # removing marked position
                self.to_be_marked_list.remove(m)

                # finding the position to be marked in 2d list
                if int(m) % 3 == 0:
                    p1 = int(m) // 3 - 1
                    p2 = 2
                else:
                    p1 = int(m) // 3
                    p2 = int(m) % 3 - 1

                # marking the position
                self.g_map[p1][p2] = "❌" if self.chance == 1 else "⭕"
                # checking if somebody win or not or its a draw
                self.status = self.win_or_not(self.g_map)

                if self.status == "":
                    # shifting the chance
                    self.chance = abs(self.chance - 1)

                    out1 = self.list_to_string(self.g_map)
                    out2 = f"{str(driver.get_contact_from_id(self.players[self.chance]).push_name)} your turn now."

                elif self.status == "draw":
                    out1 = self.list_to_string(self.g_map)
                    out2 = f"Its a Draw 🤕 \n{str(driver.get_contact_from_id(self.players[0]).push_name)} {str(driver.get_contact_from_id(self.players[1]).push_name)}"

                else:
                    out1 = self.list_to_string(self.g_map)
                    out2 = f"{str(driver.get_contact_from_id(self.status).push_name)} won the match 🎉🎉"

                driver.chat_send_message(message.chat_id, out1 + "\n" + out2)
            else:
                driver.chat_send_message(message.chat_id, "Place is already marked or invalid!")
        else:
            driver.chat_send_message(message.chat_id, "Not your chance boi 🤧")

    def win_or_not(self, l):
        if l[0][0] == l[0][1] and l[0][0] == l[0][2] and l[0][0] != "⬜":
            return self.players[1] if l[0][0] == "❌" else self.players[0]
        elif l[1][0] == l[1][1] and l[1][0] == l[1][2] and l[1][0] != "⬜":
            return self.players[1] if l[1][0] == "❌" else self.players[0]
        elif l[2][0] == l[2][1] and l[2][0] == l[2][2] and l[2][0] != "⬜":
            return self.players[1] if l[2][0] == "❌" else self.players[0]
        elif l[0][0] == l[1][0] and l[0][0] == l[2][0] and l[0][0] != "⬜":
            return self.players[1] if l[0][0] == "❌" else self.players[0]
        elif l[0][1] == l[1][1] and l[0][1] == l[2][1] and l[0][1] != "⬜":
            return self.players[1] if l[0][1] == "❌" else self.players[0]
        elif l[0][2] == l[1][2] and l[0][2] == l[2][2] and l[0][2] != "⬜":
            return self.players[1] if l[0][2] == "❌" else self.players[0]
        elif l[0][0] == l[1][1] and l[0][0] == l[2][2] and l[0][0] != "⬜":
            return self.players[1] if l[0][0] == "❌" else self.players[0]
        elif l[0][2] == l[1][1] and l[0][2] == l[2][0] and l[0][2] != "⬜":
            return self.players[1] if l[0][2] == "❌" else self.players[0]
        elif len(self.to_be_marked_list) == 0:
            return "draw"
        else:
            return ""

    def current_match(self, driver, message):
        out1 = self.list_to_string(self.g_map)
        out2 = f"{str(driver.get_contact_from_id(self.players[self.chance]).push_name)} your turn now."

        driver.chat_send_message(message.chat_id, out1 + "\n" + out2)


class GFG:
    # function for getting the code
    def gfg(self, driver, message, wd, win1, win2):
        ch = 0
        try:

            srh = message.content
            srh = list(srh.split("#"))  # splitting the message in tag,question,and language
            if len(srh) == 4:
                srh_title = srh[2]
                srh_lang = srh[3]
                srh_lang = srh_lang.capitalize()
            elif len(srh) == 3:
                srh_title = srh[2]
                srh_lang = ""
            else:
                driver.chat_send_message(message.chat_id, "Wrong syntax")
                ch = 1
            if ch == 0:
                wd.switch_to.window(win1)
                a = wd.find_element_by_name('q')  # finding the google search box
                a.clear()
                a.send_keys(f"{str(srh_title)} code gfg in {str(srh_lang)}")
                a.send_keys(Keys.ENTER)  # pressing enter key to search
                b = wd.find_elements_by_css_selector(".g a")  # selecting all the links shown in google result
                got_it = False
                for i in range(len(b)):
                    link = b[i].get_attribute('href')
                    print(link)
                    if "www.geeksforgeeks.org" in str(link):  # selecting the first link that is from gfg
                        got_it = True
                        break
                if got_it == True:
                    wd.switch_to.window(win2)
                    page = wd.get(str(link))  # opening the link in second tab if we got it

                    soup = BeautifulSoup(wd.page_source, 'html.parser')

                    # get the all the code on the page with there language label by using ids of html
                    to_lang = soup.findAll("li", {"class": "responsive-tabs__list__item"})
                    if len(to_lang) == 0:
                        to_lang = soup.findAll("h2", {"class": "tabtitle"})
                    k = soup.findAll("td", {"class": "code"})

                    get_code = False
                    p = ""
                    if len(to_lang) == 0 and len(k) != 0:  # if code is there but without language label
                        p = k[0].text
                        get_code = True
                        driver.chat_send_message(message.chat_id, p)

                    for i in range(
                            len(to_lang)):  # getting the required code in given language if it is there on the page

                        # getting the code as string from the divs
                        all_divmix = k[0].findAll("div", {"class": "container"})
                        p = ""
                        for j in all_divmix:
                            for l in j:
                                p += l.text + "\n"

                        if not str(to_lang[i].text):
                            # getting the code as string from the divs
                            all_divmix = k[i].findAll("div", {"class": "container"})
                            p = ""
                            for j in all_divmix:
                                for l in j:
                                    p += l.text + "\n"

                            driver.chat_send_message(message.chat_id, p)
                            get_code = True
                            break
                        if str(srh_lang) in str(to_lang[i].text):
                            # getting the code as string from the divs
                            all_divmix = k[i].findAll("div", {"class": "container"})
                            p = ""
                            for j in all_divmix:
                                for l in j:
                                    p += l.text + "\n"

                            print(to_lang[i].text)

                            driver.chat_send_message(message.chat_id, p)
                            get_code = True
                            break
                    if get_code == False:
                        driver.chat_send_message(
                            message.chat_id,
                            f"Code not in {srh_lang} language or code not found"
                            + "\n"
                            + p,
                        )

                else:
                    driver.chat_send_message(message.chat_id, "No data in GFG")
        except Exception as ex:
            print(ex)


class matcher:

    def __init__(self, driver, message, diff=4):
        self.diff = diff
        if diff % 2 != 0:
            self.diff += 1
        # count to check whether player won or not
        self.corr = 0

        # to check given guessing pair is valid or not
        self.match_numbers = []
        for i in range(1, diff + 1):
            self.match_numbers.extend(str(i) + str(j) for j in range(1, diff + 1))
        # time variable to check how much time it take to complete the game
        self.tim = time.time()

        # hidden layer boxes
        self.map_cov = [["📦" for _ in range(diff + 1)] for _ in range(diff + 1)]
        self.map_cov[0][0] = " "
        for i in range(1, diff + 1):
            self.map_cov[0][i] = f"  {str(i)}  "
            self.map_cov[i][0] = str(i)

        # it will the actual map of fig
        self.map = [["." for _ in range(diff + 1)] for _ in range(diff + 1)]
        self.map[0][0] = " "
        for i in range(1, diff + 1):
            self.map[0][i] = f"  {str(i)}  "
            self.map[i][0] = str(i)

        # list to choose random position
        ram = []
        for i in range(diff):
            ram.extend([i, j] for j in range(diff))
        # choosing random  fig index from emojis list
        ran_fig_list = random.sample(range(len(emojis)), (diff * diff) // 2)

        # filling the map with fig
        for i in range(len(ran_fig_list)):
            ran_fig = emojis[ran_fig_list[i]]

            # putting the same figure in two different position in the map of figures
            ran_pos = random.choice(ram)
            self.map[ran_pos[0] + 1][ran_pos[1] + 1] = ran_fig
            ram.remove(ran_pos)

            ran_pos2 = random.choice(ram)
            self.map[ran_pos2[0] + 1][ran_pos2[1] + 1] = ran_fig
            ram.remove(ran_pos2)

        out2 = self.list_to_string(self.map_cov)
        driver.chat_send_message(message.chat_id, "Game Started!!" + "\n" + out2+"\nSend #help_match see the controls.")

    def list_to_string(self, li):
        p = [' '.join(li[j]) for j in range(len(li))]
        return '\n'.join(p)

    def guess(self, driver, message, v1, v2):
        if v1 not in self.match_numbers or v2 not in self.match_numbers:
            driver.chat_send_message(message.chat_id, "Wrong input or pairs already chosen! Check again")

        else:

            l1 = list(map(int, v1))
            l2 = list(map(int, v2))

            if self.map[l1[0]][l1[1]] == self.map[l2[0]][l2[1]]:
                self.match_numbers.remove(v1)
                self.match_numbers.remove(v2)
                self.corr += 2

                if self.corr == self.diff * self.diff:
                    t_taken = str((time.time() - self.tim) // 60) + " minutes\n"
                    out = self.list_to_string(self.map)
                    driver.chat_send_message(message.chat_id,
                                         "*Wow! You won!!!*" + "\nin " + t_taken + "\n" + out)


                else:
                    self.map_cov[l1[0]][l1[1]] = self.map[l1[0]][l1[1]]
                    self.map_cov[l2[0]][l2[1]] = self.map[l2[0]][l2[1]]

                    out = self.list_to_string(self.map_cov)
                    driver.chat_send_message(message.chat_id, "Right! Continue\n" + out)
            else:
                self.map_cov[l1[0]][l1[1]] = self.map[l1[0]][l1[1]]
                self.map_cov[l2[0]][l2[1]] = self.map[l2[0]][l2[1]]
                out = self.list_to_string(self.map_cov)
                driver.chat_send_message(message.chat_id, "Nope! Wrong Pair" + "\n" + out)

                self.map_cov[l1[0]][l1[1]] = "📦"
                self.map_cov[l2[0]][l2[1]] = "📦"
                out = self.list_to_string(self.map_cov)
                driver.chat_send_message(message.chat_id, "Try Again!" + "\n" + out)

    def current_game(self, driver, message):
        out = self.list_to_string(self.map_cov)
        driver.chat_send_message(message.chat_id, "Your current game!\n" + out)


# class for minesweeper game
class mine:

    def __init__(self, driver, message, diff=4):

        # store visited mines
        self.vis = set()

        # store lose or win status
        self.status = ""

        # hidden map grid
        self.mine_cov_map = [["🔳" for _ in range(10)] for _ in range(10)]
        self.mine_cov_map[0][0] = " "
        for i in range(1, 10):
            self.mine_cov_map[0][i] = f"  {str(i)}  "
            self.mine_cov_map[i][0] = str(i)

        # map with bombs
        self.bomb_map = [[" " for _ in range(10)] for _ in range(10)]
        self.bomb_map[0][0] = " "
        for i in range(1, 10):
            self.bomb_map[0][i] = f"  {str(i)}  "
            self.bomb_map[i][0] = str(i)

        # number of bombs
        self.diff = diff * 3

        # list of chosen position by player
        self.to_be_chosen = []

        # creating list of index pair of a map to choose diff pos for bombs
        k = []
        for i in range(1, 10):
            for j in range(1, 10):
                # adding index pair in k to use it for finding sample
                k.append([i, j])
                # adding element in chosen list
                self.to_be_chosen.append(str(i) + str(j))
        self.ran_pos = random.sample(k, self.diff)
        print(self.ran_pos)

        for i in self.ran_pos:
            self.bomb_map[i[0]][i[1]] = "💣"
        out = self.listtostring(self.mine_cov_map)
        driver.chat_send_message(message.chat_id, "Game started! Best of luck 😁\n\n" + out)

    def choose(self, driver, message, ch):
        print(ch, "chhhh")

        if ch not in self.to_be_chosen:

            driver.chat_send_message(message.chat_id, "You have already chosen this box or it is invalid! 😐")

        else:

            ch = list(map(int, ch))

            # checking it is bomb or not
            if self.bomb_map[ch[0]][ch[1]] != " ":
                self.to_be_chosen.remove(self.to_str(ch[0], ch[1]))
                for i in self.ran_pos:
                    self.mine_cov_map[i[0]][i[1]] = "💣"
                out = self.listtostring(self.mine_cov_map)
                driver.chat_send_message(message.chat_id, "Oops! You lose the game ☹\n" + out)
                self.status = "Lose"

            else:
                que = [ch]
                self.vis.add(str(ch[0]) + str(ch[1]))
                while que:

                    pos = que[0]
                    que.pop(0)
                    q = []
                    i = pos[0]
                    j = pos[1]
                    flag = 0

                    # sw pos check
                    p1 = i + 1
                    p2 = j + 1
                    q, flag = self.check_adjacent_bomb(p1, p2, q, flag)

                    # s pos check
                    p1 = i + 1
                    p2 = j
                    q, flag = self.check_adjacent_bomb(p1, p2, q, flag)

                    # se pos check
                    p1 = i + 1
                    p2 = j - 1
                    q, flag = self.check_adjacent_bomb(p1, p2, q, flag)

                    # east pos check
                    p1 = i
                    p2 = j - 1
                    q, flag = self.check_adjacent_bomb(p1, p2, q, flag)

                    # ne pos check
                    p1 = i - 1
                    p2 = j - 1
                    q, flag = self.check_adjacent_bomb(p1, p2, q, flag)

                    # n pos check
                    p1 = i - 1
                    p2 = j
                    q, flag = self.check_adjacent_bomb(p1, p2, q, flag)

                    # nw pos check
                    p1 = i - 1
                    p2 = j + 1
                    q, flag = self.check_adjacent_bomb(p1, p2, q, flag)

                    # w pos check
                    p1 = i
                    p2 = j + 1
                    q, flag = self.check_adjacent_bomb(p1, p2, q, flag)

                    self.to_be_chosen.remove(self.to_str(i, j))
                    if flag == 0:
                        self.mine_cov_map[i][j] = "⚪"
                        que += q
                    else:
                        self.mine_cov_map[i][j] = emoj[flag - 1]
                if len(self.to_be_chosen) == self.diff:
                    for i in self.ran_pos:
                        self.mine_cov_map[i[0]][i[1]] = "🚩"
                    out = self.listtostring(self.mine_cov_map)
                    driver.chat_send_message(message.chat_id, "Wow! You have won 🎉🎉\n\n" + out)
                    self.status = "Won"
                else:
                    out = self.listtostring(self.mine_cov_map)
                    driver.chat_send_message(message.chat_id, "Good, Continue 🤫 \n\n" + out)

    def mark_pos(self, driver, message, ch, m):
        if ch in self.to_be_chosen:
            ch = list(map(int, ch))

            if m == 1:
                self.mine_cov_map[ch[0]][ch[1]] = "🚩"
            elif m == 0:
                self.mine_cov_map[ch[0]][ch[1]] = "🔳"
        else:
            driver.chat_send_message(message.chat_id, "It's already mined")
        out = self.listtostring(self.mine_cov_map)
        driver.chat_send_message(message.chat_id, "Marked/Unmarked\n\n" + out)

    def check_adjacent_bomb(self, p1, p2, que, flag):
        if self.check_notout_bound_pos(p1, p2):
            if self.bomb_map[p1][p2] == " ":
                st = self.to_str(p1, p2)
                if st not in self.vis:
                    que.append([p1, p2])
                    self.vis.add(st)
            else:
                flag += 1
        return [que, flag]

    def to_str(self, p1, p2):
        return str(p1) + str(p2)

    def check_notout_bound_pos(self, q, r):
        return q >= 1 and q <= 9 and r >= 1 and r <= 9

    def listtostring(self, li):
        s = [''.join(li[i]) for i in range(len(li))]
        s = "\n".join(s)
        return s


class compiler:

    def __init__(self, clientId, clientSec):
        self.r = pydoodle.Compiler(clientId=clientId,
                                   clientSecret=clientSec)

        self.inuse = 0

    def run(self, driver, message, lang, code):
        self.code = code
        self.lang = lang.lower()
        self.languages = ['ada', 'bash', 'bc', 'brainfuck', 'c', 'c-99', 'clisp', 'clojure', 'cobol', 'coffeescript',
                          'cpp',
                          'cpp17', 'csharp', 'd', 'dart', 'elixir', 'erlang', 'factor', 'falcon', 'fantom', 'forth',
                          'fortran', 'freebasic', 'fsharp', 'gccasm', 'go', 'groovy', 'hack', 'haskell', 'icon',
                          'intercal',
                          'java', 'jlang', 'kotlin', 'lolcode', 'lua', 'mozart', 'nasm', 'nemerle', 'nim', 'nodejs',
                          'objc',
                          'ocaml', 'octave', 'pascal', 'perl', 'php', 'picolisp', 'pike', 'prolog', 'python2',
                          'python3', 'r',
                          'racket', 'rhino', 'ruby', 'rust', 'scala', 'scheme', 'smalltalk', 'spidermonkey', 'sql',
                          'swift',
                          'tcl', 'unlambda', 'vbn', 'verilog', 'whitespace', 'yabasic']

        if lang.lower() in self.languages:

            self.inuse = 1

            result = self.r.execute(script=self.code, language=self.lang)
            res = list(result.output)[0]

            if "Timeout" in res:
                driver.chat_send_message(message.chat_id,"Program Timeout:\nCauses can be INFINITE LOOP or INPUT STATEMENTS")
            else:
                try:
                    driver.wapi_functions.sendMessageWithMentions(message.chat_id, "Output-:\n" + res + "\n\n" + str(
                        result.cpuTime) + " s", "")
                except:
                    driver.chat_send_message(message.chat_id,"Output-:\n" + res + "\n\n" + str(result.cpuTime) + " s")

            self.inuse = 0
        else:
            driver.chat_send_message(
                message.chat_id,
                f"Sorry!! Only Language supported are:-\n {' ,'.join(self.languages)} ",
            )


class ludo:

    def __init__(self,driver,msg,p1,p2,p3=None,p4=None):
        self.dice_got = 0
        self.gstart=1
        self.six_counter=0
        #final result
        self.fin_res="Match ended!!\nFinal Result:\n"

        #to check whether the player have thrown the dice or not
        self.dthrow=0
        #ludo board
        self.ludo_board=[["⬜" for i in range(11)]for j in range(11)]

        #a counter to choose whose player turn is now
        self.idx=0
        #filling the green color places
        for r,c in [[0,0],[0,1],[0,2],[0,3],[1,0],[1,3],[2,0],[2,3],[3,0],[3,1],[3,2],[3,3],[4,1],[5,1],[5,2],[5,3],[5,4]]:
            self.ludo_board[r][c]="🟩"

        # filling the yellow color places
        for r,c in [[0,7],[0,8],[0,9],[0,10],[1,5],[1,6],[1,7],[1,10],[2,5],[2,7],[2,10],[3,5],[3,7],[3,8],[3,9],[3,10],[4,5]]:
            self.ludo_board[r][c] = "🟨"

        # filling the red color places
        for r,c in [[5,6],[5,7],[5,8],[5,9],[6,9],[7,7],[7,8],[7,9],[7,10],[8,7],[8,10],[9,7],[9,10],[10,7],[10,8],[10,9],[10,10]]:
            self.ludo_board[r][c]="🟥"

        # filling the blue color places
        for r,c in [[6,5],[7,0],[7,1],[7,2],[7,3],[7,5],[8,0],[8,3],[8,5],[9,0],[9,3],[9,4],[9,5],[10,0],[10,1],[10,2],[10,3]]:
            self.ludo_board[r][c] = "🟦"
        self.ludo_board[5][5]="🏠"

        #list of places which are safe/full stop
        self.safe=[[4,1],[9,4],[1,6],[6,9]]
        #list 1 which conains pieces if they are on same places
        self.stoplist_1=[]
        # list 2 which conains pieces if they are on same places
        self.stoplist_2 = []
        # list 3 which conains pieces if they are on same places
        self.stoplist_3 = []
        # list 4 which conains pieces if they are on same places
        self.stoplist_4 = []
        #creating ludo_player objects dict
        self.players={p1:"",p2:""}
        if p3!=None:
            self.players[p3]=""
        if p4!=None:
            self.players[p4]=""

        n = len(self.players)
        self.li_players = random.sample(list(self.players.keys()), n)
        self.c=['b','y','g','r']

        #initilising the ludo's pieces
        for i in range(n):
            p=self.li_players[i]
            if self.c[i]=='b':
                path=[[i,4] for i in range(9,5,-1)]+\
                     [[6,j] for j in range(3,-1,-1)]+\
                     [[5,0],[4,0]]+\
                     [[4,j] for j in range(1,5)]+\
                     [[i,4] for i in range(3,-1,-1)]+\
                     [[0,5],[0,6]]+\
                     [[i,6] for i in range(1,5)]+\
                     [[4,j] for j in range(7,11)]+\
                     [[5,10],[6,10]]+\
                     [[6,j] for j in range(9,5,-1)]+\
                     [[i,6] for i in range(7,11)]+\
                     [[10,5]]+\
                     [[i,5] for i in range(9,4,-1)]
                g1=ludo_goti(9,1,9,4,'b',1,path)
                g2=ludo_goti(8,2,9,4,'b',2,path)

                self.players[p]=ludo_player(self.c[i],0,g1,g2,1)
            elif self.c[i]=='g':
                path = [[4, j] for j in range(1, 5)] + \
                       [[i, 4] for i in range(3, -1, -1)] + \
                       [[0, 5], [0, 6]] + \
                       [[i, 6] for i in range(1, 5)] + \
                       [[4, j] for j in range(7, 11)] + \
                       [[5, 10], [6, 10]] + \
                       [[6, j] for j in range(9, 5, -1)] + \
                       [[i, 6] for i in range(7, 11)] + \
                       [[10, 5],[10,4]] + \
                       [[i, 4] for i in range(9, 5, -1)] + \
                       [[6, j] for j in range(3, -1, -1)] + \
                       [[5, 0]]+\
                       [[5,j] for j in range(1,6)]
                g1 = ludo_goti(2, 1, 4, 1,'g',1,path)
                g2 = ludo_goti(1, 2, 4, 1,'g',2,path)
                self.players[p] = ludo_player(self.c[i], 0, g1, g2)
            elif self.c[i]=='y':
                path = [[i, 6] for i in range(1, 5)] + \
                       [[4, j] for j in range(7, 11)] + \
                       [[5, 10], [6, 10]] + \
                       [[6, j] for j in range(9, 5, -1)] + \
                       [[i, 6] for i in range(7, 11)] + \
                       [[10, 5],[10,4]] + \
                       [[i, 4] for i in range(9, 5, -1)] + \
                       [[6, j] for j in range(3, -1, -1)] + \
                       [[5, 0],[4,0]]+ \
                       [[4, j] for j in range(1, 5)] + \
                       [[i, 4] for i in range(3, -1, -1)] + \
                       [[0, 5]]+\
                       [[i,5] for i in range(1,6)]
                g1 = ludo_goti(1, 8, 1, 6,'y',1,path)
                g2 = ludo_goti(2, 9, 1, 6,'y',2,path)
                self.players[p] = ludo_player(self.c[i], 0, g1, g2)
            elif self.c[i]=='r':
                path = [[6, j] for j in range(9, 5, -1)] + \
                       [[i, 6] for i in range(7, 11)] + \
                       [[10, 5],[10,4]] + \
                       [[i, 4] for i in range(9, 5, -1)] + \
                       [[6, j] for j in range(3, -1, -1)] + \
                       [[5, 0],[4,0]]+ \
                       [[4, j] for j in range(1, 5)] + \
                       [[i, 4] for i in range(3, -1, -1)] + \
                       [[0, 5],[0,6]]+ \
                       [[i, 6] for i in range(1, 5)] + \
                       [[4, j] for j in range(7, 11)] + \
                       [[5, 10]] + \
                       [[5,j] for j in range(9,4,-1)]
                g1 = ludo_goti(8, 9, 6, 9,'r',1,path)
                g2 = ludo_goti(9, 8, 6, 9,'r',2,path)
                self.players[p] = ludo_player(self.c[i], 0, g1, g2)

        self.temp_board=copy.deepcopy(self.ludo_board)

        #placing the ludo's pieces at house of respective colour
        self.place_pieces()
        #drawing the board in chat
        self.draw_board(driver,msg)
        out="Your pieces colour:\n"

        #color to player dict
        self.c_to_p=dict()
        self.cur_player_list=self.li_players[:]
        #printing which color is related to which player
        for i in self.players.keys():
            self.c_to_p[self.temp_board[self.players[i].g1.cur_x][self.players[i].g1.cur_y]]=i
            out+=self.temp_board[self.players[i].g1.cur_x][self.players[i].g1.cur_y]+": "+str(driver.get_contact_from_id(i).push_name)+" \n"
        driver.chat_send_message(msg.chat_id,out)
        if n>2:
            self.li_players[1],self.li_players[2]=self.li_players[2],self.li_players[1]
        driver.chat_send_message(msg.chat_id,str(driver.get_contact_from_id(self.li_players[0]).push_name)+" your turn.\nThrow the dice using #rdice command.")

    #placing the ludo's pieces at their new positions
    def place_pieces(self):
        print(self.players)
        self.temp_board=copy.deepcopy(self.ludo_board)
        for value in self.players.values():
            value.g1.draw_goti(self.temp_board)
            value.g2.draw_goti(self.temp_board)

    #function to draw the board and send it
    def draw_board(self,driver,msg,ext=""):
        s=ext+"\n"
        for i in range(len(self.temp_board)):
            s+=''.join(self.temp_board[i])+"\n"
        driver.chat_send_message(msg.chat_id,s)


    #function to check piece can move or not
    def can_move(self,piece):
        if self.dice_got!=6 and  piece.cur_x==piece.home_x and piece.cur_y==piece.home_y:
            return False
        if self.dice_got>len(piece.path)-piece.step-1:
            return False
        return True


    #function to throw dice
    def dice(self,driver,msg,a):
        self.dice_got=random.choice([1,2,3,4,5,6,6,6])
        if a!=0:
            self.dice_got=a
        self.dthrow=1
        d=self.dice_got
        if d==1:driver.chat_send_message(msg.chat_id,"🎲1️⃣🎲")
        if d == 2: driver.chat_send_message(msg.chat_id,"🎲2️⃣🎲")
        if d == 3: driver.chat_send_message(msg.chat_id,"🎲3️⃣🎲")
        if d == 4: driver.chat_send_message(msg.chat_id,"🎲4️⃣🎲")
        if d == 5: driver.chat_send_message(msg.chat_id,"🎲5️⃣🎲")
        if d == 6: driver.chat_send_message(msg.chat_id,"🎲6️⃣🎲")
        if self.dice_got==6:
            self.six_counter+=1
            if self.six_counter==3:
                driver.chat_send_message(msg.chat_id,"Three six in a row\nSorry! Your chance will skip")
                self.helper(driver,msg)
                return
        c_pi1=self.players[msg.sender.id].g1
        c_pi2=self.players[msg.sender.id].g2


        #to check whether both pieces of player are at home or not
        if not self.can_move(c_pi1) and not self.can_move(c_pi2):

            driver.wapi_functions.sendMessage(msg.chat_id,"Bad Luck 😓")
            self.helper(driver,msg)


        elif self.can_move(c_pi1) and self.can_move(c_pi2):
            driver.wapi_functions.sendMessage(msg.chat_id, "Choose your piece to move!")
        else:

            if self.can_move(c_pi1):
                self.move_piece_helper(driver,msg,c_pi1)
            else:
                self.move_piece_helper(driver,msg,c_pi2)




    #second helper function when dice throw 6
    def helper2(self,driver,msg):

        self.dthrow = 0
        self.dice_got = 0
        # placing the ludo's pieces at house of respective colour
        self.place_pieces()

        #if safe places are filled with more than two pieces
        self.ext=""
        if len(self.stoplist_1)>1:
            self.temp_board[self.safe[0][0]][self.safe[0][1]]="🔥"
            self.ext+="\n🔥 :"
            for pe in self.stoplist_1:
                self.ext+=" "+pe.get_piece()
        if len(self.stoplist_2) > 1:
            self.temp_board[self.safe[1][0]][self.safe[1][1]] = "🎃"
            self.ext += "\n🎃 :"
            for pe in self.stoplist_2:
                self.ext += " " + pe.get_piece()
        if len(self.stoplist_3)>1:
            self.temp_board[self.safe[2][0]][self.safe[2][1]]="✨"
            self.ext+="\n✨ :"
            for pe in self.stoplist_3:
                self.ext+=" "+pe.get_piece()
        if len(self.stoplist_4)>1:
            self.temp_board[self.safe[3][0]][self.safe[3][1]]="🌎"
            self.ext+="\n🌎 :"
            for pe in self.stoplist_4:
                self.ext+=" "+pe.get_piece()
        # drawing the board in chat
        self.draw_board(driver,msg,self.ext)
        driver.chat_send_message(msg.chat_id, str(driver.get_contact_from_id(self.cur_player_list[
            self.idx % len(self.cur_player_list)]).push_name) + " your turn")

    #helper function to move forward
    def helper(self,driver,msg):
        self.players[msg.sender.id].chance = 0
        self.idx += 1
        self.players[self.cur_player_list[self.idx % len(self.cur_player_list)]].chance = 1
        self.dthrow = 0
        self.dice_got=0
        self.six_counter=0
        # placing the ludo's pieces at house of respective colour
        self.place_pieces()
        # if safe places are filled with more than two pieces
        self.ext = ""
        if len(self.stoplist_1) > 1:
            self.temp_board[self.safe[0][0]][self.safe[0][1]] = "🔥"
            self.ext += "\n🔥 :"
            for pe in self.stoplist_1:
                self.ext += " " + pe.get_piece()
        if len(self.stoplist_2) > 1:
            self.temp_board[self.safe[1][0]][self.safe[1][1]] = "🎃"
            self.ext += "\n🎃 :"
            for pe in self.stoplist_2:
                self.ext += " " + pe.get_piece()
        if len(self.stoplist_3) > 1:
            self.temp_board[self.safe[2][0]][self.safe[2][1]] = "✨"
            self.ext += "\n✨ :"
            for pe in self.stoplist_3:
                self.ext += " " + pe.get_piece()
        if len(self.stoplist_4) > 1:
            self.temp_board[self.safe[3][0]][self.safe[3][1]] = "🌎"
            self.ext += "\n🌎 :"
            for pe in self.stoplist_4:
                self.ext += " " + pe.get_piece()

        # drawing the board in chat
        self.draw_board(driver,msg,self.ext)
        driver.chat_send_message(msg.chat_id, str(driver.get_contact_from_id(self.cur_player_list[
                                                                                            self.idx % len(
                                                                                                self.cur_player_list)]).push_name) + " your turn")


    def piece_present(self, pie, msg):
        co = [pie.cur_x, pie.cur_y]
        r = []
        for pl in self.cur_player_list:
            if pl != msg.sender.id:
                if [self.players[pl].g1.cur_x, self.players[pl].g1.cur_y] == co:
                    r.append(self.players[pl].g1)
                if [self.players[pl].g2.cur_x, self.players[pl].g2.cur_y] == co:
                    r.append(self.players[pl].g2)
        if len(r) != 0:
            return r
        return None


    def move_piece_helper(self,driver,msg,c_piece):

        if c_piece.cur_x==c_piece.home_x and c_piece.cur_y==c_piece.home_y :
            if self.dice_got==6:
                c_piece.cur_x,c_piece.cur_y=c_piece.path[c_piece.step][0],c_piece.path[c_piece.step][1]
                self.place_safe(c_piece)
                self.helper2(driver,msg)

            else:
                driver.chat_send_message(msg.chat_id,"This piece is not open yet 🙄.Choose other one")
        elif self.dice_got>len(c_piece.path)-c_piece.step-1:
            driver.chat_send_message(msg.chat_id,"Can't move 😅 \nYou require {} or less for this piece.\nMove the other piece".format(len(c_piece.path)-c_piece.step-1))

        else:
            print(self.dice_got , len(c_piece.path) ,c_piece.step + 1)
            c_piece.step+=self.dice_got

            c_piece.cur_x, c_piece.cur_y = c_piece.path[c_piece.step][0], c_piece.path[c_piece.step][1]
            self.place_safe(c_piece)


            if [c_piece.cur_x, c_piece.cur_y] not in self.safe:
                present= self.piece_present(c_piece,msg)

                if present!=None:
                    for p in present:
                        p.cur_x,p.cur_y=p.home_x,p.home_y
                        p.step=0

                    driver.wapi_functions.sendMessage(msg.chat_id,"You got a kill!!")
                    self.helper2(driver, msg)
                else:
                    if c_piece.step==len(c_piece.path)-1:
                        c_piece.win=1
                        c_piece.cur_x=-1
                        c_piece.cur_y=-1
                        if self.players[msg.sender.id].g1.win==1 and self.players[msg.sender.id].g2.win==1:
                            self.cur_player_list.remove(msg.sender.id)
                            driver.chat_send_message(msg.chat_id,"Congo 🎉 You got rank {}".format(len(self.li_players)-len(self.cur_player_list)))
                            self.fin_res+="{} : Rank {}\n".format(str(driver.get_contact_from_id(msg.sender.id).push_name),len(self.li_players)-len(self.cur_player_list))
                            if len(self.cur_player_list)==1:
                                self.fin_res+="{} : Rank {}\n".format(str(driver.get_contact_from_id(self.cur_player_list[0]).push_name),len(self.li_players)-len(self.cur_player_list)+1)
                                self.cur_player_list=[]

                                driver.chat_send_message(msg.chat_id,self.fin_res)
                            else:
                                self.helper(driver,msg)
                        else:
                            self.helper2(driver,msg)
                    else:
                        if self.dice_got==6:
                            self.helper2(driver,msg)
                        else:
                            self.helper(driver,msg)
            else:
                if self.dice_got == 6:
                    self.helper2(driver, msg)
                else:
                    self.helper(driver, msg)

    def place_safe(self, c_piece):
        if [c_piece.cur_x, c_piece.cur_y] in self.safe:
            print("safe yess")
            if self.safe[0] == [c_piece.cur_x, c_piece.cur_y]:
                self.stoplist_1.append(c_piece)

            elif self.safe[1] == [c_piece.cur_x, c_piece.cur_y]:
                self.stoplist_2.append(c_piece)
            elif self.safe[2] == [c_piece.cur_x, c_piece.cur_y]:
                self.stoplist_3.append(c_piece)
            else:
                self.stoplist_4.append(c_piece)
            print(self.stoplist_1, self.stoplist_2, self.stoplist_3, self.stoplist_4)

        else:
            if c_piece in self.stoplist_1: self.stoplist_1.remove(c_piece)
            if c_piece in self.stoplist_2: self.stoplist_2.remove(c_piece)
            if c_piece in self.stoplist_3: self.stoplist_3.remove(c_piece)
            if c_piece in self.stoplist_4: self.stoplist_4.remove(c_piece)


    #function to move the piece
    def move_piece(self,driver,msg,pi):
        if pi=='h':

            c_piece=self.players[msg.sender.id].g2
        else:
            c_piece=self.players[msg.sender.id].g1

        if c_piece.cur_x<0:
            driver.chat_send_message(msg.chat_id,"This piece is already in the house.Choose other")
        else:
            self.move_piece_helper(driver,msg,c_piece)

    #function to send current ludo board
    def current_board(self,driver,msg):
        self.draw_board(driver,msg,self.ext)

    #quit ludo
    def quit(self,driver,msg):
        self.cur_player_list.remove(msg.sender.id)
        if self.players[msg.sender.id].chance==1 and len(self.cur_player_list)!=1:
            self.helper(driver, msg)

        del self.players[msg.sender.id]







class ludo_goti:
    def __init__(self,home_x,home_y,start_x,start_y,colour,p,path):
        self.p=p
        self.path=path
        self.step=0
        self.home_x=home_x
        self.home_y=home_y
        self.start_x=start_x
        self.start_y=start_y
        self.cur_x=self.home_x
        self.cur_y=self.home_y
        self.start=0
        self.win=0
        self.colour=colour
    def draw_goti(self,board):
        c=self.colour
        if self.cur_x<0:
            return
        if c=='b':
            if self.p==1:
                board[self.cur_x][self.cur_y]="🔵"
            else:
                board[self.cur_x][self.cur_y] = "💙"
        elif c=='y':
            if self.p==1:
                board[self.cur_x][self.cur_y]="🟡"
            else:
                board[self.cur_x][self.cur_y] = "💛"
        elif c=='g':
            if self.p==1:
                board[self.cur_x][self.cur_y]="🟢"
            else:
                board[self.cur_x][self.cur_y]="💚"

        elif c=='r':
            if self.p==1:
                board[self.cur_x][self.cur_y]="🔴"
            else:
                board[self.cur_x][self.cur_y]="❤️"
    def get_piece(self):
        c = self.colour
        if c == 'b':
            if self.p == 1:
                return( "🔵")
            else:
                return("💙")
        elif c == 'y':
            if self.p == 1:
                return "🟡"
            else:
                return "💛"
        elif c == 'g':
            if self.p == 1:
                return "🟢"
            else:
               return "💚"

        elif c == 'r':
            if self.p == 1:
                return "🔴"
            else:
                return "❤️"
class ludo_player:
    def __init__(self,colour,status,g1,g2,chance=0):
        self.colour=colour
        self.status=status
        self.g1=g1
        self.g2=g2
        self.chance=chance

#class for crypto commands
class crypto:

    def __init__(self):
        self.crypto_com_base_url="https://min-api.cryptocompare.com/data"
        self.coingecko_base_url='https://api.coingecko.com/api/v3/'
        self.cyptopanic_base_url='https://cryptopanic.com/api/v1/posts/?'

        self.coin_dict=dict()
        coin_list=requests.get('{}/coins/list'.format(self.coingecko_base_url)).json()
        for c in coin_list:
            if c['symbol'] not in self.coin_dict:
                self.coin_dict[c['symbol']]=[c['id']]
            else:
                self.coin_dict[c['symbol']].append(c['id'])
    def price(self,driver,msg,coin):
        coin=coin.lower()
        if coin in self.coin_dict:
            out = ""
            for j in range(len(self.coin_dict[coin])):
                try:
                    data=requests.get(self.coingecko_base_url+'simple/price/?ids={}&vs_currencies=usd,inr,btc'.format(self.coin_dict[coin][j])).json()
                    out+="*_" +self.coin_dict[coin][j].upper()+"_*"+"\n\n"
                    symbol=["$","₹",""]
                    i=0
                    for curr,price in data[self.coin_dict[coin][j]].items():
                        out+="*{}{}* = *{}{}* \n\n".format(coin.upper(),curr.upper(),symbol[i],('%.14f'%float(price)).rstrip('0').rstrip('.'))
                        i+=1
                    out+="\n\n"
                except Exception as e:
                    print(e)
                    driver.chat_send_message(msg.chat_id,"Some error occurred!!")
            out=out.strip()
            driver.chat_send_message(msg.chat_id, out)
        else:
            driver.chat_send_message(msg.chat_id,"*Coin not found!!*")

    def news(self,driver,chat_id,api,topic):
        try:
            if topic!='':
                data=requests.get(self.cyptopanic_base_url+'auth_token={}&public=true&kind=news&currencies={}'.format(api,topic)).json()
            else:
                data=requests.get(self.cyptopanic_base_url+'auth_token={}&public=true&kind=news'.format(api)).json()
            out="*Latest Crypto News*\n\n"
            for news in data['results']:
                out+="🌟 "+news['slug'].replace("-"," ")+"\n\n"
            if out=='':
                driver.chat_send_message(chat_id,"*No Data Found!!*")
            else:
                driver.chat_send_message(chat_id,out)

        except Exception as e:
            print(e)
            driver.chat_send_message(chat_id,"Sry!!Some error occurred")

    def detail(self,driver,msg,coin):
        if coin in self.coin_dict:
            data=requests.get(self.coingecko_base_url+'coins/markets?vs_currency=usd&ids={}&order=market_cap_desc&per_page=100&page=1&sparkline=true&price_change_percentage=1h'.format(self.coin_dict[coin][0])).json()
            if len(data)==0:
                driver.chat_send_message(msg.chat_id,"*No Data Found*")
            else:
                out="----------------- *{}* ---------------------\n\n".format(self.coin_dict[coin][0].upper())
                data=data[0]
                out+='*Name:* {}\n\n*Current Price:* {}\n\n*Market Cap:* {}\n\n*Market Cap Rank:* {}\n\n*Total Volume:* {}\n\n*24h High:* {}\n\n*24h Low:* {}\n\n*24h Price Change:* {}\n\n*24h Price Change%:* {}\n\n*1h Price Change%:* {}\n\n*24h Market Cap Change:* {}\n\n*24h Market Cap Change%:* {}\n\n*Circulating Supply:* {}\n\n*Total Supply:* {}\n\n*Max Supply:* {}\n\n*ATH Value:* {}\n'.format(data['name'],data['current_price'],data['market_cap'],data['market_cap_rank'],data['total_volume'],data['high_24h'],data['low_24h'],data['price_change_24h'],data['price_change_percentage_24h'],data['price_change_percentage_1h_in_currency'],data['market_cap_change_24h'],data['market_cap_change_percentage_24h'],data['circulating_supply'],data['total_supply'],data['max_supply'],data['ath'])
                driver.chat_send_message(msg.chat_id,out)
        else:
            driver.chat_send_message(msg.chat_id,"*Coin not found!!*")

    def mmi(self,driver,msg):
        response = requests.get("https://alternative.me/crypto/fear-and-greed-index.png")
        file = open("mmi.png", "wb")
        file.write(response.content)
        file.close()
        driver.send_media("mmi.png",msg.chat_id,"")


#class for calculator
class Calculator:

        def calc(self,driver,msg,s):
            try:
                a = eval(s)
                driver.chat_send_message(msg.chat_id,str(a))
            except Exception as e:
                driver.chat_send_message(msg.chat_id,str(e))

class db_data_to_dictionary:

    def get(self,out,n,k):
        if out[0] == None:
            d = dict()
        else:
            out = out[0]
            l = len(out) // n
            i = 0
            j = l*k
            d = dict()
            for i in range(l):
                id=out[i].replace("\"","")
                if out[j].isnumeric():
                    val=int(out[j])
                else:
                    val=out[j]
                d[id] = val
                i += 1
                j += 1
        return d


class cmd_suggesstion:
    def __init__(self, allcmds):
        self.all_cmd = allcmds

    def suggest(self, driver,message, cmd):

        cmd_len = len(cmd)

        lcs_list=[]
        comman_chr_list = []

        for cm in self.all_cmd:

            # Longest comman subsequence between the given command and all cmds code

            cm_len = len(cm)

            L = [[-1] * (cm_len + 1) for i in range(cmd_len + 1)]

            for i in range(cmd_len + 1):
                for j in range(cm_len + 1):
                    if i == 0 or j == 0:
                        L[i][j] = 0
                    elif cmd[i - 1] == cm[j - 1]:
                        L[i][j] = L[i - 1][j - 1] + 1
                    else:
                        L[i][j] = max(L[i - 1][j], L[i][j - 1])

            lcs_list.append([L[cmd_len][cm_len]/cm_len,cm])


            #code to check number of comman character in cmd with all cmds
            curr_cmd=list(cmd)
            curr_li_cmd=list(cm)

            coun=0
            for i in curr_li_cmd:
                if i in curr_cmd:
                    curr_cmd.remove(i)
                    coun+=1

            comman_chr_list.append([coun/cm_len,cm])

        #sorting both the list to get high priority length at top
        lcs_list.sort()
        comman_chr_list.sort()

        fin_list= {lcs_list[-1][1], lcs_list[-2][1], comman_chr_list[-1][1], comman_chr_list[-2][1]}
        out=",".join(fin_list)

        driver.chat_send_message(message.chat_id,"Wrong Command!!\nI think you mean one of the following:\n"+out+"\nFor more commands use #help")





# class for quiting the program (admin only according to calling if condition)
class quit_bot:
    def quit(self, driver, wd):
        wd.quit()  # quiting chrome driver
        driver.quit()  # quiting WhatsappApi driver

# Code written by Kailash Sharma
