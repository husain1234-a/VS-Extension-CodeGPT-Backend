import { TerminalReader } from './terminal';

const reader = new TerminalReader();
const input = await reader.readLine('Enter something: ');