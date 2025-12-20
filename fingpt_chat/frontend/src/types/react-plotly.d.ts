/** Type declarations for react-plotly.js */
declare module 'react-plotly.js' {
  import { Component } from 'react';
  
  interface PlotParams {
    data: any[];
    layout?: any;
    config?: any;
    revision?: number;
    onInitialized?: (figure: any, graphDiv: HTMLElement) => void;
    onUpdate?: (figure: any, graphDiv: HTMLElement) => void;
    onPurge?: (figure: any, graphDiv: HTMLElement) => void;
    onError?: (err: Error) => void;
    debug?: boolean;
    useResizeHandler?: boolean;
    style?: React.CSSProperties;
    className?: string;
  }
  
  export default class Plot extends Component<PlotParams> {}
}

