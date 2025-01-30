import * as readline from 'readline';

export class TerminalReader {
    private rl: readline.Interface;

    constructor() {
        this.rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
    }

    async readLine(prompt: string = ''): Promise<string> {
        return new Promise((resolve) => {
            this.rl.question(prompt, (answer: string) => {
                resolve(answer);
            });
        });
    }

    async readMultipleLines(delimiter: string = 'EOF'): Promise<string[]> {
        const lines: string[] = [];
        
        console.log(`Enter multiple lines (type '${delimiter}' to finish):`);
        
        return new Promise((resolve) => {
            this.rl.on('line', (input: string) => {
                if (input === delimiter) {
                    this.rl.removeAllListeners('line');
                    resolve(lines);
                } else {
                    lines.push(input);
                }
            });
        });
    }

    async readSecure(prompt: string = 'Enter secure input: '): Promise<string> {
        const stdin = process.stdin;
        const stdout = process.stdout;
        
        stdin.setRawMode(true);
        stdout.write(prompt);

        let input = '';
        
        return new Promise((resolve) => {
            stdin.on('data', (data) => {
                const char = data.toString();

                if (char === '\b' || char === '\x7f') {
                    if (input.length > 0) {
                        input = input.slice(0, -1);
                        stdout.write('\b \b');
                    }
                    return;
                }

                if (char === '\r' || char === '\n') {
                    stdout.write('\n');
                    stdin.setRawMode(false);
                    stdin.removeAllListeners('data');
                    resolve(input);
                    return;
                }

                input += char;
                stdout.write('*');
            });
        });
    }

    close(): void {
        this.rl.close();
    }
}

async function main() {
    const reader = new TerminalReader();

    try {
        const name = await reader.readLine('Enter your name: ');
        console.log('Hello,', name);

        const lines = await reader.readMultipleLines();
        console.log('You entered:', lines);

        const password = await reader.readSecure('Enter password: ');
        console.log('Password received (length):', password.length);

    } finally {
        reader.close();
    }
}

main().catch(console.error);