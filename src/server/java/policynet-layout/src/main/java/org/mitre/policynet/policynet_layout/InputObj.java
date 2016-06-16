package org.mitre.policynet.policynet_layout;

import java.util.List;
import java.util.Map;

public class InputObj {
	private List<ParsedEdge> edges;
	private Map<String, String> config;
	/**
	 * @return the edges
	 */
	public List<ParsedEdge> getEdges() {
		return edges;
	}

	/**
	 * @param edges the edges to set
	 */
	public void setEdges(List<ParsedEdge> edges) {
		this.edges = edges;
	}

	/**
	 * @return the config
	 */
	public Map<String, String> getConfig() {
		return config;
	}

	/**
	 * @param config the config to set
	 */
	public void setConfig(Map<String, String> config) {
		this.config = config;
	}
	
}
