
export interface ResearchItem {
    id: string;
    type: 'video' | 'web' | 'doc';
    title: string;
    content: string;
    timestamp: number;
    metadata?: any;
}

export interface IntelligenceBlock {
    title: string;
    summary: string;
    chapters?: { title: string; timestamp: string }[];
    entities?: string[];
    citations?: { source: string; text: string }[];
}
