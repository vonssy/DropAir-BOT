from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from colorama import *
from datetime import datetime
from fake_useragent import FakeUserAgent
import asyncio, time, json, base64, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class DropAir:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://dropair.io/?ref=9S9TD6",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": FakeUserAgent().random
        }

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}DropAir - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def hide_token(self, token):
        hide_token = token[:3] + '*' * 3 + token[-3:]
        return hide_token
    
    def decode_token(self, token: str):
        try:
            header, payload, signature = token.split(".")
            decoded_payload = base64.urlsafe_b64decode(payload + "==").decode("utf-8")
            parsed_payload = json.loads(decoded_payload)
            username = parsed_payload["username"]
            exp_time = parsed_payload["exp"]
            return f"@{username}", exp_time
        except Exception as e:
            return None, None
    
    async def user_info(self, token: str):
        url = "https://dropair.io/api/user"
        headers = {
            **self.headers,
            "Cookie": f"auth-token={token}",
            "Content-Type": "application/json"
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=120)) as session:
                async with session.get(url=url, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
        except (Exception, ClientResponseError) as e:
            return None
        
    async def complete_tasks(self, token: str, task_id: str):
        url = "https://dropair.io/api/tasks"
        data = json.dumps({'taskId':task_id})
        headers = {
            **self.headers,
            "Cookie": f"auth-token={token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=120)) as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    response.raise_for_status()
                    return await response.json()
        except (Exception, ClientResponseError) as e:
            return None
    
    async def process_accounts(self, token: str, exp_time: int):
        exp_time_wib = datetime.fromtimestamp(exp_time, pytz.utc).astimezone(wib).strftime('%x %X %Z')
        if int(time.time()) > exp_time:
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Token Expired {Style.RESET_ALL}"
            )
            return

        self.log(
            f"{Fore.CYAN + Style.BRIGHT}Status    :{Style.RESET_ALL}"
            f"{Fore.GREEN + Style.BRIGHT} Token Active {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Expired at {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{exp_time_wib}{Style.RESET_ALL}"
        )

        user = await self.user_info(token)
        if user:
            balance = user.get("totalPoints", "N/A")

        self.log(
            f"{Fore.CYAN + Style.BRIGHT}Balance   :{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {balance} DROP {Style.RESET_ALL}"
        )

        self.log(
            f"{Fore.CYAN + Style.BRIGHT}Task Lists:{Style.RESET_ALL}"
        )

        task_ids = ["daily-task", "follow-twitter-drop3io", "tweet-about-drop", "join-telegram"]
        title = None
        for task_id in task_ids:
            if task_id == "daily-task":
                title = "Daily Check-In"
            elif task_id == "follow-twitter-drop3io":
                title = "Follow on X (Twitter)"
            elif task_id == "tweet-about-drop":
                title = "Tweet about DROP"
            elif task_id == "join-telegram":
                title = "Join Telegram"
            else:
                title = "Untitled"

            complete = await self.complete_tasks(token, task_id)
            if complete and complete['success']:
                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}    -> {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{title}{Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT} Is Completed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Reward {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{complete['points']} DROP{Style.RESET_ALL}"
                )
            else:
                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}    -> {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{title}{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} Is Already Completed {Style.RESET_ALL}"
                )
                
            await asyncio.sleep(1)

    async def main(self):
        try:
            with open('tokens.txt', 'r') as file:
                tokens = [line.strip() for line in file if line.strip()]
            
            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
                )
                
                separator = "=" * 25
                for token in tokens:
                    if token:
                        username, exp_time = self.decode_token(token)
                        if username and exp_time:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                            )
                            await self.process_accounts(token, exp_time)
                            await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*60)
                seconds = 12 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'tokens.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = DropAir()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] DropAir - BOT{Style.RESET_ALL}                                       "                              
        )