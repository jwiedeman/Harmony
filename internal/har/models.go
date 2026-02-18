package har

// HAR 1.2 specification structs

type HAR struct {
	Log Log `json:"log"`
}

type Log struct {
	Version string  `json:"version"`
	Creator Creator `json:"creator"`
	Entries []Entry `json:"entries"`
}

type Creator struct {
	Name    string `json:"name"`
	Version string `json:"version"`
}

type Entry struct {
	StartedDateTime string   `json:"startedDateTime"`
	Request         Request  `json:"request"`
	Response        Response `json:"response"`
	Timings         Timings  `json:"timings"`
}

type Request struct {
	Method      string      `json:"method"`
	URL         string      `json:"url"`
	HTTPVersion string      `json:"httpVersion"`
	Headers     []NameValue `json:"headers"`
	QueryString []NameValue `json:"queryString"`
	PostData    *PostData   `json:"postData,omitempty"`
}

type Response struct {
	Status     int         `json:"status"`
	StatusText string      `json:"statusText"`
	Headers    []NameValue `json:"headers"`
	Content    Content     `json:"content"`
}

type Content struct {
	Size     int    `json:"size"`
	MimeType string `json:"mimeType"`
	Text     string `json:"text,omitempty"`
}

type NameValue struct {
	Name  string `json:"name"`
	Value string `json:"value"`
}

type PostData struct {
	MimeType string      `json:"mimeType"`
	Text     string      `json:"text"`
	Params   []NameValue `json:"params,omitempty"`
}

type Timings struct {
	Send    float64 `json:"send"`
	Wait    float64 `json:"wait"`
	Receive float64 `json:"receive"`
}

// NetworkEvent is the normalized output from parsing a HAR entry.
type NetworkEvent struct {
	Method      string
	URL         string
	Headers     map[string]string
	QueryParams map[string]string
	PostBody    string
	PostParams  map[string]string
}
